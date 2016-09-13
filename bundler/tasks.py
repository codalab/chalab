import os
import shutil
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


def gen_documentation(output_dir, challenge):
    doc = challenge.documentation
    if doc is None:
        return {}

    mapping = challenge_to_mappings(challenge)
    pages = doc.pages
    r = {}

    for p in pages:
        r[p.name] = p.name + '.html'
        p.render(mapping)

        with open(path.join(output_dir, p.name + '.html'), 'w') as f:
            f.write(p.rendered)


def gen_reference(output_dir, dataset, phase_id):
    pass


def gen_phases(output_dir, challenge):
    dataset = challenge.dataset

    return {'1':
                {'datasets':
                     {'1':
                          {'name': dataset.name,
                           'description': dataset.description,
                           'reference': gen_reference(output_dir, dataset, '1')}}}}


def gen_logo(output_dir, challenge):
    assert challenge.logo is not None, 'logo should be set'

    logo = challenge.logo
    name = path.basename(logo.name)

    try:
        logo.open()
        copy_file_field(logo.file, path.join(output_dir, name))
    finally:
        logo.close()

    return name


def create_bundle(output_dir, challenge):
    html = gen_documentation(output_dir, challenge)
    phases = gen_phases(output_dir, challenge)

    data = {
        'title': challenge.title,
        'description': challenge.description,
        # 'image':  TODO
        'html': html,
        'phases': phases
    }

    if challenge.logo:
        logo = gen_logo(output_dir, challenge)
        data['logo'] = logo

    with open(path.join(output_dir, 'competition.yaml'), 'w') as f:
        yaml.dump(data, f)


def create_archive(data_dir, output_dir):
    a = shutil.make_archive(path.join(output_dir, 'bundle'), 'zip',
                            root_dir=data_dir, base_dir='.')
    return a


def save_archive(archive, challenge, bundle_task):
    with open(archive, 'rb') as f:
        bundle_task.output.save('bundle_%s_%s.zip' % (challenge.pk, bundle_task.pk), File(f))


@shared_task
def bundle(bundle_task):
    challenge = bundle_task.challenge

    with tmp_dirs(challenge) as (data, output):
        bundle_task.state = bundle_task.STARTED
        bundle_task.save()

        create_bundle(data, challenge)
        a = create_archive(data, output)
        save_archive(a, challenge, bundle_task)

    bundle_task.state = bundle_task.FINISHED
    bundle_task.closed = timezone.now()
    bundle_task.save()
