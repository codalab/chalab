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


@contextmanager
def bundle(challenge):
    with tasks.tmp_dirs(challenge) as (data, output):
        tasks.create_bundle(data, challenge)

        with open(path.join(data, 'competition.yaml'), 'r') as f:
            data_yaml = yaml.load(f)

        ls = os.listdir(data)

        yield data_yaml, ls


def test_bundler_set_finished_state(random_challenge):
    c = random_challenge.challenge
    bt = models.BundleTaskModel.create(c)
    tasks.bundle(bt)
    assert bt.state == models.BundleTaskModel.FINISHED


def test_create_bundle_adds_yaml(random_challenge):
    c = random_challenge.challenge

    with bundle(c) as (yaml, ls):
        assert 'competition.yaml' in ls


def test_create_bundle_adds_documentations(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (yaml, ls):
        assert set([x for x in ls if x.endswith('.html')]) == DEFAULT_DOCS


def test_create_bundle_preserve_yaml_title(challenge_ready):
    c = challenge_ready.challenge

    with bundle(c) as (yaml, ls):
        assert yaml['title'] == c.title


def test_create_archive_creates_zip_file(random_challenge):
    c = random_challenge.challenge

    with tasks.tmp_dirs(c) as (data, output):
        tasks.create_bundle(data, c)
        a = tasks.create_archive(data, output)
        assert path.exists(a)


def test_bundler_set_output_zipfile(random_challenge):
    c = random_challenge.challenge
    bt = models.BundleTaskModel.create(c)
    tasks.bundle(bt)

    output = bt.output
    assert output is not None

    with ZipFile(output.path, 'r') as z:
        files = z.namelist()

        assert 'competition.yaml' in files


def test_bundler_doesnt_bundle_itself(random_challenge):
    c = random_challenge.challenge
    bt = models.BundleTaskModel.create(c)
    tasks.bundle(bt)

    output = bt.output
    assert output is not None

    with ZipFile(output.path, 'r') as z:
        files = z.namelist()

        assert 'bundle.zip' not in files
