import time

import pytest

from tests.shortcuts import SClient
from tests.tools import assert_redirects, sreverse

pytestmark = pytest.mark.django_db


def test_bundler_disallow_build_on_incomplete_challenge(random_challenge):
    client = SClient.logged(random_challenge.desc)
    r = client.post('wizard:challenge:bundler:build', pk=random_challenge.challenge.pk)

    assert r.status_code == 400
    assert b'The challenge is not ready to be bundled' in r.content


def test_bundler_build_redirects_to_challenge(c):
    r = c.post('wizard:challenge:bundler:build', pk=c.pk)
    assert_redirects(r, sreverse('wizard:challenge', pk=c.pk))


def test_download_bundle_returns_404_by_default(c):
    r = c.get('wizard:challenge:bundler:download', pk=c.pk)
    assert r.status_code == 404


def test_download_bundle_returns_redirect_to_file_when_ready(c):
    r = c.post('wizard:challenge:bundler:build', pk=c.pk)
    time.sleep(5)
    r = c.get('wizard:challenge:bundler:download', pk=c.pk)

    assert r.status_code == 302
