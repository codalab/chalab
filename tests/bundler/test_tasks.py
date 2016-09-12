import os
from os import path
from zipfile import ZipFile

import pytest

from bundler import models
from bundler import tasks

pytestmark = pytest.mark.django_db


def test_bundler_set_finished_state(random_challenge):
    c = random_challenge.challenge
    bt = models.BundleTaskModel.create(c)
    tasks.bundle(bt)
    assert bt.state == models.BundleTaskModel.FINISHED


def test_create_bundle_adds_yaml(random_challenge):
    c = random_challenge.challenge

    with tasks.tmp_dirs(c) as (data, output):
        tasks.create_bundle(data, c)
        assert 'competition.yaml' in os.listdir(data)


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
