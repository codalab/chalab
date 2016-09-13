import os
from contextlib import contextmanager
from os import path
from zipfile import ZipFile

import pytest
import yaml

from bundler import models
from bundler import tasks

pytestmark = pytest.mark.django_db

DEFAULT_DOCS = {'overview.html', 'evaluation.html', 'data.html', 'terms_and_conditions.html'}


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
def bundle(challenge):
    with tasks.tmp_dirs(challenge) as (data, output):
        tasks.create_bundle(data, challenge)

        with open(path.join(data, 'competition.yaml'), 'r') as f:
            data_yaml = yaml.load(f)

        ls = os.listdir(data)

        yield data, data_yaml, ls


@contextmanager
def zip(path):
    with ZipFile(path, 'r') as z:
        yield z, z.namelist()


def test_bundler_set_finished_state(challenge_ready):
    c = challenge_ready.challenge
    bt = models.BundleTaskModel.create(c)
    tasks.bundle(bt)
    assert bt.state == models.BundleTaskModel.FINISHED


def test_create_bundle_adds_yaml(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (output_path, yaml, ls):
        assert 'competition.yaml' in ls


def test_create_bundle_adds_documentations(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (output_path, yaml, ls):
        assert set([x for x in ls if x.endswith('.html')]) == DEFAULT_DOCS


def test_create_bundle_preserve_yaml_title(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (output_path, yaml, ls):
        assert yaml['title'] == c.title


def test_create_bundle_adds_dataset(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (output_path, yaml, ls):
        assert has(yaml, ['phases', '1', 'datasets', '1'])


def test_create_bundle_adds_logo(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (output_path, yaml, ls):
        assert 'logo' in yaml
        assert yaml['logo'] in ls


def test_create_bundle_no_logo_works(challenge_ready):
    c = challenge_ready.challenge
    c.logo = None
    c.save()

    with bundle(c) as (output_path, yaml, ls):
        assert 'logo' not in yaml


@pytest.mark.skip
def test_create_bundle_adds_reference_data(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (output_path, yaml, ls):
        name = has(yaml, ['phases', '1', 'datasets', '1', 'reference_data'], get_value=True)
        assert name in ls

        with zip(path.join(output_path, name)) as (z, ls):
            assert 'answer.txt' in ls
            assert 'metadata' in ls


def test_create_archive_creates_zip_file(challenge_ready):
    c = challenge_ready.challenge

    with tasks.tmp_dirs(c) as (data, output):
        tasks.create_bundle(data, c)
        a = tasks.create_archive(data, output)
        assert path.exists(a)


def test_bundler_set_output_zipfile(challenge_ready):
    c = challenge_ready.challenge
    bt = models.BundleTaskModel.create(c)
    tasks.bundle(bt)

    output = bt.output
    assert output is not None

    with zip(output.path) as (z, ls):
        assert 'competition.yaml' in ls


def test_bundler_doesnt_bundle_itself(challenge_ready):
    c = challenge_ready.challenge
    bt = models.BundleTaskModel.create(c)
    tasks.bundle(bt)

    output = bt.output
    assert output is not None

    with ZipFile(output.path, 'r') as z:
        files = z.namelist()

        assert 'bundle.zip' not in files
