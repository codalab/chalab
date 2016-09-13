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


def gen_documentation(output_dir, challenge):
    doc = challenge.documentation
    if doc is None:
        return {}

    mapping = challenge_to_mappings(challenge)
    pages = doc.pages
    r = {}

    for p in pages:
        r[p.title] = p.title + '.html'
        p.render(mapping)

        with open(path.join(output_dir, p.title + '.html'), 'w') as f:
            f.write(p.rendered)


def create_bundle(output_dir, challenge):
    html = gen_documentation(output_dir, challenge)

    data = {
        'title': challenge.title,
        'description': challenge.description,
        # 'image':  TODO
        'html': html
    }

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
