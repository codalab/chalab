import os
import shutil
from contextlib import contextmanager
from os import path
from tempfile import TemporaryDirectory

from celery import shared_task
from django.core.files import File


@contextmanager
def tmp_dirs(challenge):
    with TemporaryDirectory(prefix='bundle_%s' % challenge.pk) as d:
        d_data = path.join(d, 'data')
        d_output = path.join(d, 'output')

        os.mkdir(d_data)
        os.mkdir(d_output)

        yield d_data, d_output


def create_bundle(output_dir, challenge):
    with open(path.join(output_dir, 'competition.yaml'), 'w') as f:
        f.write('helloworld')


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
    bundle_task.save()
