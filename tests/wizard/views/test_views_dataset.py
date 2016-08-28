import pytest
from django.test import Client
from django.urls import reverse

from tests.tools import make_request, assert_redirects, html, query
from tests.wizard.models.tools import make_samples_datasets
from wizard import views as wiz

pytestmark = pytest.mark.django_db


def test_open_data_redirects_to_picker(random_challenge):
    pk = random_challenge.challenge.pk
    url = reverse('wizard:challenge:data', kwargs={'pk': random_challenge.challenge.pk})
    request = make_request(url, user=random_challenge.user)

    response = wiz.ChallengeDataUpdate.as_view()(request, pk=pk)

    assert_redirects(response, reverse('wizard:challenge:data.pick', kwargs={'pk': pk}),
                     fetch_redirect_response=False)


def test_data_picker_shows_public_dataset(random_challenge):
    pk = random_challenge.challenge.pk

    url = reverse('wizard:challenge:data.pick', kwargs={'pk': random_challenge.challenge.pk})
    request = make_request(url, user=random_challenge.user)

    response = wiz.data_picker(request, pk=pk)
    h = html(response)

    assert h.select_one('.module')['id'] == 'data-picker'
    assert 'Which dataset' in h.select_one('.module h1').text


def test_data_picker_shows_public_datasets_empty(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    c = Client()
    assert c.login(username=d.username, password=d.password)
    q = query('wizard:challenge:data.pick', c=c, kwargs={'pk': pk})

    assert q.response.context['public_datasets'].count() == 0


def test_data_picker_shows_public_datasets_with_a_couple(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    (d1, d2) = make_samples_datasets()

    c = Client()
    assert c.login(username=d.username, password=d.password)
    q = query('wizard:challenge:data.pick', c=c, kwargs={'pk': pk})

    pds = q.response.context['public_datasets']

    assert pds.count() == 2
    assert d1 in pds
    assert d2 in pds


def test_data_picker_shows_form_pick_public_datasets(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = make_samples_datasets()

    c = Client()
    assert c.login(username=d.username, password=d.password)
    q = query('wizard:challenge:data.pick', c=c, kwargs={'pk': pk})

    s = q.html.select_one('.pick .public form select')
    options = s.select('option')
    options_txt = [x.text for x in options]

    assert len(options) == len(samples)
    for s in samples:
        assert s.name in options_txt


def test_data_picker_when_select_public_dataset_returns_to_regular_data(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = make_samples_datasets()
    s = samples[0]

    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:data.pick', kwargs={'pk': pk}),
               {'kind': 'public', 'dataset': s.pk})

    assert_redirects(r, reverse('wizard:challenge:data', kwargs={'pk': pk}))


def test_data_picker_once_selected_redirects_to_regular_data(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = make_samples_datasets()
    s = samples[0]

    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:data.pick', kwargs={'pk': pk}),
               {'kind': 'public', 'dataset': s.pk})

    r = c.get(reverse('wizard:challenge:data.pick', kwargs={'pk': pk}))
    assert_redirects(r, reverse('wizard:challenge:data', kwargs={'pk': pk}))
