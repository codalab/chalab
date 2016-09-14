import os
from contextlib import contextmanager
from os import path
from unittest.mock import create_autospec
from zipfile import ZipFile

import yaml

from bundler import models
from bundler import tasks


def remove_logo(challenge_tuple):
    c = challenge_tuple.challenge
    c.logo = None
    c.save()


def has(yaml, path, get_value=False):
    current_p = ''

    for p in path:
        current_p += '/' + str(p)

        assert p in yaml, "path %s couldn't be found" % current_p
        yaml = yaml[p]

    if get_value:
        return yaml
    else:
        return True


@contextmanager
def zip(path):
    with ZipFile(path, 'r') as z:
        yield z, z.namelist()

mock_bundle = create_autospec(models.BundleTaskModel, return_value=None)

@contextmanager
def create_bundle(challenge_tuple):
    challenge = challenge_tuple.challenge
    with tasks.tmp_dirs(challenge) as (data, output):
        tasks.create_bundle(mock_bundle, data, challenge)

        with open(path.join(data, 'competition.yaml'), 'r') as f:
            data_yaml = yaml.load(f)

        ls = os.listdir(data)

        yield data, data_yaml, ls


@contextmanager
def bundle(challenge_tuple):
    c = challenge_tuple.challenge
    bt = models.BundleTaskModel.create(c)

    tasks.bundle(bt)

    assert bt.output is not None, "bundler didn't complete, output is None"

    yield bt, bt.output
