import pytest
from django.test import Client
from django.urls import reverse

from tests.tools import assert_redirects
from tests.wizard.models.tools import make_samples_datasets
from wizard import models

pytestmark = pytest.mark.django_db


def get_without_dataset_redirects(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.get(reverse('wizard:challenge:task', kwargs={'pk': pk}))

    assert_redirects(r, reverse('wizard:challenge:data.pick', kwargs={'pk': pk}))


def get_with_dataset_returns_200(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = make_samples_datasets()
    s = samples[0]

    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:data.pick', kwargs={'pk': pk}),
               {'kind': 'public', 'dataset': s.pk})

    r = c.get(reverse('wizard:challenge:task', kwargs={'pk': pk}))

    assert r.status_code == 200


def test_pick_public_dataset_automatically_sets_task(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = make_samples_datasets()
    s = samples[0]

    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:data.pick', kwargs={'pk': pk}),
               {'kind': 'public', 'dataset': s.pk})

    r = c.get(reverse('wizard:challenge:task', kwargs={'pk': pk}))

    x = models.TaskModel.objects.get(dataset=s)
    assert r.context['task'] == x
