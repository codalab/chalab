import time

import pytest
from django.test import Client
from django.urls import reverse

from tests.tools import assert_redirects

pytestmark = pytest.mark.django_db


def test_bundler_build_redirects_to_challenge(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:bundler:build', kwargs={'pk': pk}))
    assert_redirects(r, reverse('wizard:challenge', kwargs={'pk': pk}))


def test_download_bundle_returns_404_by_default(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.get(reverse('wizard:challenge:bundler:download', kwargs={'pk': pk}))
    assert r.status_code == 404


def test_download_bundle_returns_redirect_to_file_when_ready(challenge_ready):
    pk = challenge_ready.challenge.pk
    d = challenge_ready.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:bundler:build', kwargs={'pk': pk}))
    time.sleep(5)
    r = c.get(reverse('wizard:challenge:bundler:download', kwargs={'pk': pk}))

    assert r.status_code == 302
