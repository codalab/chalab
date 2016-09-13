import pytest

from tests.tools import assert_redirects, sreverse
from tests.wizard.models.tools import make_samples_datasets
from wizard import models

pytestmark = pytest.mark.django_db


def test_get_without_dataset_redirects(cb):
    r = cb.get('wizard:challenge:task', pk=cb.pk)
    assert_redirects(r, sreverse('wizard:challenge:data.pick', pk=cb.pk))


def test_get_with_dataset_returns_200(cb):
    samples = make_samples_datasets()
    s = samples[0]

    cb.post('wizard:challenge:data.pick', pk=cb.pk,
            data={'kind': 'public', 'dataset': s.pk})

    r = cb.get('wizard:challenge:task', pk=cb.pk)

    assert r.status_code == 200


def test_pick_public_dataset_automatically_sets_task(cb):
    samples = make_samples_datasets()
    s = samples[0]

    cb.post('wizard:challenge:data.pick', pk=cb.pk,
            data={'kind': 'public', 'dataset': s.pk})

    r = cb.get('wizard:challenge:task', pk=cb.pk)
    x = models.TaskModel.objects.get(dataset=s)
    assert r.context['task'] == x
