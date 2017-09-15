import os
import random
import shutil
import traceback
from contextlib import contextmanager
from os import path
from tempfile import TemporaryDirectory

import yaml
from celery import shared_task
from django.core.files import File
from django.utils import timezone

from chalab.tools import fs
from wizard import resources
from wizard.models import challenge_to_mappings

PROTOCOL_MAX_SUBMISSIONS = 100
PROTOCOL_MAX_SUBMISSIONS_PER_DAY = 5
PROTOCOL_EXECUTION_TIME_LIMIT = 500


@contextmanager
def tmp_dirs(challenge):
    with TemporaryDirectory(prefix='bundle_%s' % challenge.pk) as d:
        d_data = path.join(d, 'data')
        d_output = path.join(d, 'output')

        os.mkdir(d_data)
        os.mkdir(d_output)

        yield d_data, d_output


def copy_file_field(file_desc, dest_path):
    with open(dest_path, 'wb') as f:
        shutil.copyfileobj(file_desc, f)


def gen_documentation(bt, output_dir, challenge):
    bt.add_log('Generate the documentation')
    doc = challenge.documentation
    if doc is None:
        return {}

    mapping = challenge_to_mappings(challenge)
    pages = doc.pages
    r = {}

    for p in pages:
        bt.add_log('Export page: %s' % p.name)
        r[p.name] = p.name + '.html'
        p.render(mapping)

        with open(path.join(output_dir, p.name + '.html'), 'w') as f:
            f.write(p.rendered)

    return r


def gen_reference(output_dir, dataset, phase_id):
    pass


def load_metadata_files(data, tmp_dir, name):
    for ext, ext_name in [(data.input, 'feat'), (data.target, 'label')]:
        for axis, axis_name in [(ext.cols, 'cols'), (ext.rows, 'rows')]:
            if axis is not None:
                for content, cont_name in [(axis.types, 'type'),
                                           (axis.names, 'name'),
                                           (axis.doc, 'info')]:
                    if content is not None:
                        filename = '%s_%s.%s' % (name, ext_name, cont_name)

                        if cont_name == 'info':
                            filename = '%s_public.info' % name

                        content.raw_content.open()
                        copy_file_field(content.raw_content,
                                        path.join(tmp_dir, filename))
                        content.raw_content.close()


def create_info_file(challenge, tmp_dir):
    data, task = challenge.dataset, challenge.task
    name = task.name

    filename = '%s_public.info' % name

    to_write = [
        'name = %s' % name,
        'metric = %s' % challenge.metric.name,
        'feat_num = %s' % data.input.cols.count,
        'target_num = %s' % data.target.cols.count,
        'train_num = %s' % task.input_train.rows.count,
        'valid_num = %s' % task.input_valid.rows.count,
        'test_num = %s' % task.input_test.rows.count,
        'is_sparse = %s' % (1 if data.input.is_sparse else 0)
    ]

    to_write = [line + '\n' for line in to_write]

    with open(path.join(tmp_dir, filename), 'w') as f:
        f.writelines(to_write)


def gen_dev_phase(bt, output_dir, challenge, task, protocol, metric):
    number = 1

    bt.add_log('Create phase %s' % number)

    p = {'phasenumber': number,
         'label': protocol.dev_phase_label,
         'description': protocol.dev_phase_description,
         'start_date': protocol.dev_start_date,
         'is_scoring_only': False,
         'color': 'green',
         'execution_time_limit': PROTOCOL_EXECUTION_TIME_LIMIT,
         'max_submissions': PROTOCOL_MAX_SUBMISSIONS,
         'max_submissions_per_day': PROTOCOL_MAX_SUBMISSIONS_PER_DAY}

    ref_data = 'reference_data_%s' % number

    name = task.name

    # Input data is generated here, used by both phases
    input_data = 'input_data_1_2'
    # Scoring program is fixed too
    scoring_program = 'scoring_program_1_2'

    with TemporaryDirectory() as d:
        try:
            task.target_valid.raw_content.open()
            copy_file_field(task.target_valid.raw_content,
                            path.join(d, '%s_valid.solution' % name))

            zipdir(bt, output_dir, ref_data, d)
            p['reference_data'] = ref_data + '.zip'
        finally:
            task.target_valid.raw_content.close()

    with TemporaryDirectory() as d:
        try:
            task.input_train.raw_content.open()
            copy_file_field(task.input_train.raw_content,
                            path.join(d, '%s_train.data' % name))

            task.input_valid.raw_content.open()
            copy_file_field(task.input_valid.raw_content,
                            path.join(d, '%s_valid.data' % name))

            task.input_test.raw_content.open()
            copy_file_field(task.input_test.raw_content,
                            path.join(d, '%s_test.data' % name))

            task.target_train.raw_content.open()
            copy_file_field(task.target_train.raw_content,
                            path.join(d, '%s_train.solution' % name))

            load_metadata_files(challenge.dataset, d, name)

            if not os.path.isfile(path.join(d, '%s_public.info' % name)):
                create_info_file(challenge, d)

            zipdir(bt, output_dir, input_data, d)
            p['input_data'] = input_data + '.zip'
            p['public_data'] = input_data + '.zip'
        finally:
            task.input_train.raw_content.close()
            task.input_valid.raw_content.close()
            task.input_test.raw_content.close()
            task.target_train.raw_content.close()

    with fs.tmp_dir() as d:
        scoring_dir = os.path.join(d, scoring_program)
        resources.build_default_scoring(metric, scoring_dir)

        archive_path = zipdir(bt, output_dir, scoring_program, scoring_dir)
        p['scoring_program'] = os.path.basename(archive_path)

    baseline = challenge.baseline.submission
    # name = os.path.basename(baseline.path)
    name = "baseline-{0}.zip".format(challenge.id)
    try:
        bt.add_log('Load the challenge baseline')
        baseline.open()
        copy_file_field(baseline.file, path.join(output_dir, name))
        p['starting_kit'] = name
    finally:
        baseline.close()

    return p


def typed(value):
    if isinstance(value, str):
        return "'%s'" % value
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    else:
        return '%s' % value


def gen_info_file(path, content):
    lines = ['%s = %s\n' % (k, typed(v)) for k, v in content.items()]

    with open(path, 'w') as f:
        f.writelines(lines)


def gen_final_phase(bt, output_dir, challenge, task, protocol, metric):
    number = 2

    bt.add_log('Create phase %s' % number)

    p = {'phasenumber': number,
         'label': protocol.final_phase_label,
         'description': protocol.final_phase_description,
         'start_date': protocol.final_start_date,
         'is_scoring_only': False,
         'auto_migration': True,
         'color': 'purple',
         'execution_time_limit': PROTOCOL_EXECUTION_TIME_LIMIT,
         'max_submissions': PROTOCOL_MAX_SUBMISSIONS,
         'max_submissions_per_day': 0}

    ref_data = 'reference_data_%s' % number
    name = task.name

    # Input data is generated in dev phase
    input_data = 'input_data_1_2.zip'
    # Scoring program is fixed too
    scoring_program = 'scoring_program_1_2.zip'

    p['input_data'] = input_data
    p['scoring_program'] = scoring_program

    with TemporaryDirectory() as d:
        try:
            task.target_test.raw_content.open()
            copy_file_field(task.target_test.raw_content,
                            path.join(d, '%s_test.solution' % name))

            # gen_info_file(path.join(d, '%s_public.info' % name),
            #               {'metric': metric.name,
            #                'task': 'classification' if metric.classification else 'regression'})

            zipdir(bt, output_dir, ref_data, d)
            p['reference_data'] = ref_data + '.zip'
        finally:
            task.target_test.raw_content.close()

    return p


def gen_phases(bt, output_dir, challenge):
    dev_p = gen_dev_phase(bt, output_dir, challenge, challenge.task,
                          challenge.protocol, challenge.metric)

    final_p = gen_final_phase(bt, output_dir, challenge, challenge.task,
                              challenge.protocol, challenge.metric)

    return {1: dev_p, 2: final_p}


def gen_logo(bt, output_dir, challenge):
    assert challenge.logo is not None, 'logo should be set'

    logo = challenge.logo
    name = path.basename(logo.name)

    try:
        bt.add_log('Load the challenge logo')
        logo.open()
        copy_file_field(logo.file, path.join(output_dir, name))
    finally:
        logo.close()

    return name


def gen_leaderboard(challenge):
    leaderboard_Results = {'label': 'Results', 'rank': 1}

    leaderboard = {
        'leaderboards': {
            'Results': leaderboard_Results,
        },
        'columns': {
            'set1_score':
                {'leaderboard': leaderboard_Results,
                 'label': 'Prediction score',
                 'numeric_format': 4,
                 'rank': 2},
            'Duration':
                {'leaderboard': leaderboard_Results,
                 'label': 'Duration',
                 'numeric_format': 2,
                 'rank': 7}
        }
    }
    return leaderboard


def create_bundle(bt, output_dir, challenge):
    html = gen_documentation(bt, output_dir, challenge)
    phases = gen_phases(bt, output_dir, challenge)
    leaderboard = gen_leaderboard(challenge)

    data = {
        'title': challenge.title,
        'description': challenge.description,
        'html': html,
        'phases': phases,
        'leaderboard': leaderboard,
        'has_registration': False,
        'force_submission_to_leaderboard': True,
        'disallow_leaderboard_modifying': True,
        'allow_teams': False,
        'enable_detailed_results': True,
        'show_datasets_from_yaml': True,
        'allow_public_submissions': True,
        'anonymous_leaderboard': False,
        'enable_per_submission_metadata': False,
        'enable_forum': True,
        'end_date': None,
        'admin_names': 'guyon,lsenta'  # temporary default admins.
    }

    if challenge.logo:
        logo = gen_logo(bt, output_dir, challenge)
        data['image'] = logo

    bt.add_log('Dump the competition.yaml file')
    with open(path.join(output_dir, 'competition.yaml'), 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def zipdir(bt, output_dir, archive_name, data_dir):
    bt.add_log('Creating archive: %s' % archive_name)
    a = shutil.make_archive(path.join(output_dir, archive_name), 'zip',
                            root_dir=data_dir, base_dir='.')
    return a


def create_archive(bt, data_dir, output_dir):
    bt.add_log('Package to bundle directory')
    return zipdir(bt, output_dir, 'bundle', data_dir)


def save_archive(bt, archive, challenge, bundle_task):
    bt.add_log('Export the archive')
    with open(archive, 'rb') as f:
        bundle_task.output.save('bundle_%s.zip' % challenge.pk, File(f))


def generate_task_data(bundle_task, challenge):
    task = challenge.task
    data = challenge.dataset

    if task.has_content and data.fixed_split:
        bundle_task.add_log('Skipping task data splitting, fixed split')
        return

    if task.updated_at <= challenge.build_at:
        bundle_task.add_log('Skipping task data splitting, already splinted')
        return

    bundle_task.add_log('Starting task data generation, '
                        'based on dataset: %s' % data.pk)
    train, valid, test = task.train_ratio, task.valid_ratio, task.test_ratio

    bundle_task.add_log('Generating content for task: %s(%s)'
                        % (task.name, task.pk))

    size = data.input.rows.count

    train_size = int(train / 100.0 * size)
    valid_size = int(valid / 100.0 * size)
    # test_size = int(test / 100.0 * size)

    xs = list(range(size))
    random.shuffle(xs)

    train, rest = xs[:train_size], xs[train_size:]
    valid, test = rest[:valid_size], rest[valid_size:]

    input = data.input.raw_content
    target = data.target.raw_content

    input.open(), target.open()
    with fs.tmp_dir() as output:
        gen = os.path.join(output, 'gen')
        fs.mkdir(gen)
        with open(os.path.join(gen, 'gen_train.data'), 'wb') as ti, \
                open(os.path.join(gen, 'gen_train.solution'), 'wb') as tt, \
                open(os.path.join(gen, 'gen_valid.data'), 'wb') as vi, \
                open(os.path.join(gen, 'gen_valid.solution'), 'wb') as vt, \
                open(os.path.join(gen, 'gen_test.data'), 'wb') as si, \
                open(os.path.join(gen, 'gen_test.solution'), 'wb') as st:
            for i in range(size):
                li = input.readline()
                lt = target.readline()

                if i in train:
                    ti.write(li)
                    tt.write(lt)
                elif i in valid:
                    vi.write(li)
                    vt.write(lt)
                else:
                    si.write(li)
                    st.write(lt)
        task.update_from_chalearn(gen)
    input.close(), target.close()


@shared_task
def bundle(bundle_task):
    try:
        challenge = bundle_task.challenge

        with tmp_dirs(challenge) as (data, output):
            bundle_task.add_log('Starting bundler for: %s'
                                % (challenge.title,))

            bundle_task.state = bundle_task.STARTED
            bundle_task.save()

            generate_task_data(bundle_task, challenge)
            create_bundle(bundle_task, data, challenge)
            a = create_archive(bundle_task, data, output)
            save_archive(bundle_task, a, challenge, bundle_task)

        challenge.build_at = timezone.now()
        challenge.save()

        bundle_task.add_log('Set state to finished')
        bundle_task.state = bundle_task.FINISHED
        bundle_task.closed = timezone.now()
        bundle_task.save()
    except Exception as e:
        bundle_task.state = bundle_task.FAILED
        bundle_task.save()

        bundle_task.add_log('Exception: %r' % e)
        bundle_task.add_log('Traceback:\n%s' % traceback.format_exc())
        bundle_task.add_log('Set state to failed')
