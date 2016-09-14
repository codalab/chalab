import time

import pytest

from bundler import models
from tests.shortcuts import SClient
from tests.tools import assert_redirects, sreverse

pytestmark = pytest.mark.django_db


class TestBundler(object):
    def test_disallow_build_on_incomplete_challenge(self, random_challenge):
        client = SClient.logged(random_challenge.desc)
        r = client.post('wizard:challenge:bundler:build', pk=random_challenge.challenge.pk)

        assert r.status_code == 400
        assert b'The challenge is not ready to be bundled' in r.content

    def test_build_redirects_to_challenge(self, c):
        r = c.post('wizard:challenge:bundler:build', pk=c.pk)
        assert_redirects(r, sreverse('wizard:challenge', pk=c.pk))

    def test_cant_build_if_previous_is_SCHEDULED(self, c):
        bt = models.BundleTaskModel.create(c.challenge)
        bt.state = bt.SCHEDULED
        bt.save()

        r = c.post('wizard:challenge:bundler:build', pk=c.pk)

        assert r.status_code == 400
        assert b'The bundle is already being built' in r.content

    def test_cant_build_if_previous_is_STARTED(self, c):
        bt = models.BundleTaskModel.create(c.challenge)
        bt.state = bt.STARTED
        bt.save()

        r = c.post('wizard:challenge:bundler:build', pk=c.pk)

        assert r.status_code == 400
        assert b'The bundle is already being built' in r.content

    def test_cant_build_again_if_previous_is_FINISHED(self, c):
        bt = models.BundleTaskModel.create(c.challenge)
        bt.state = bt.FINISHED
        bt.save()

        r = c.post('wizard:challenge:bundler:build', pk=c.pk)
        assert_redirects(r, sreverse('wizard:challenge', pk=c.pk))

    def test_cant_build_again_if_previous_is_FAILED(self, c):
        bt = models.BundleTaskModel.create(c.challenge)
        bt.state = bt.FAILED
        bt.save()

        r = c.post('wizard:challenge:bundler:build', pk=c.pk)
        assert_redirects(r, sreverse('wizard:challenge', pk=c.pk))


class TestBundlerLogs(object):
    def test_logs_pages_returns_404_by_default(self, c):
        r = c.get('wizard:challenge:bundler:logs', pk=c.pk)
        assert r.status_code == 404

    def test_logs_pages_returns_200_when_building(self, c):
        c.post('wizard:challenge:bundler:build', pk=c.pk)

        r = c.get('wizard:challenge:bundler:logs', pk=c.pk)
        assert r.status_code == 200


class TestBundleDownload(object):
    def test_returns_404_by_default(self, c):
        r = c.get('wizard:challenge:bundler:download', pk=c.pk)
        assert r.status_code == 404

    def test_returns_redirect_to_file_when_ready(self, c):
        r = c.post('wizard:challenge:bundler:build', pk=c.pk)
        time.sleep(5)
        r = c.get('wizard:challenge:bundler:download', pk=c.pk)

        assert r.status_code == 302
