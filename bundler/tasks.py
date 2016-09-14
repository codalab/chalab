import os
import shutil
import traceback
from contextlib import contextmanager
from os import path
from tempfile import TemporaryDirectory

import yaml
from celery import shared_task
from django.core.files import File
from django.utils import timezone

from wizard.models import challenge_to_mappings


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


def gen_phases(bt, output_dir, challenge):
    dataset = challenge.dataset

    x = {'name': dataset.name}

    if dataset.description is not None:
        x['description'] = dataset.description
    # x['reference']= gen_reference(output_dir, dataset, '1')

    bt.add_log('Create phase 1')

    return {1: {'datasets': {1: x}}}


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


def create_bundle(bt, output_dir, challenge):
    html = gen_documentation(bt, output_dir, challenge)
    phases = gen_phases(bt, output_dir, challenge)

    data = {
        'title': challenge.title,
        'description': challenge.description,
        'html': html,
        'phases': phases
    }

    if challenge.logo:
        logo = gen_logo(bt, output_dir, challenge)
        data['logo'] = logo

    bt.add_log('Dump the competition.yaml file')
    with open(path.join(output_dir, 'competition.yaml'), 'w') as f:
        yaml.dump(data, f)


def create_archive(bt, data_dir, output_dir):
    bt.add_log('Package to bundle directory')
    a = shutil.make_archive(path.join(output_dir, 'bundle'), 'zip',
                            root_dir=data_dir, base_dir='.')
    return a


def save_archive(bt, archive, challenge, bundle_task):
    bt.add_log('Export the archive')
    with open(archive, 'rb') as f:
        bundle_task.output.save('bundle_%s_%s.zip' % (challenge.pk, bundle_task.pk), File(f))


@shared_task
def bundle(bundle_task):
    try:
        challenge = bundle_task.challenge

        with tmp_dirs(challenge) as (data, output):
            bundle_task.add_log('Starting bundler for: %s' % (challenge.title,))

            bundle_task.state = bundle_task.STARTED
            bundle_task.save()

            create_bundle(bundle_task, data, challenge)
            a = create_archive(bundle_task, data, output)
            save_archive(bundle_task, a, challenge, bundle_task)

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
