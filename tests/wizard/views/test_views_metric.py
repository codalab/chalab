import pytest
from django.test import Client
from django.urls import reverse

from tests.tools import make_request, assert_redirects, html, query
from tests.wizard.models import tools
from wizard import views as wiz

pytestmark = pytest.mark.django_db


def test_open_metric_redirects_to_picker(random_challenge):
    pk = random_challenge.challenge.pk
    desc = random_challenge.desc

    client = Client()
    assert client.login(username=desc.username, password=desc.password)

    r = client.get(reverse('wizard:challenge:metric', kwargs={'pk': pk}))

    assert_redirects(r, reverse('wizard:challenge:metric.pick', kwargs={'pk': pk}))


def test_metric_picker_shows_public_metrics_picker_ui(random_challenge):
    pk = random_challenge.challenge.pk

    url = reverse('wizard:challenge:metric.pick', kwargs={'pk': pk})
    request = make_request(url, user=random_challenge.user)

    response = wiz.metric_picker(request, pk=pk)
    h = html(response)

    assert h.select_one('.module')['id'] == 'metric-picker'
    assert 'Which metric' in h.select_one('.module h1').text


def test_metric_picker_has_public_metric_in_context(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    s = tools.make_samples_metrics()

    c = Client()
    assert c.login(username=d.username, password=d.password)

    q = query('wizard:challenge:metric.pick', c=c, kwargs={'pk': pk})
    pds = q.response.context['public_metrics']

    assert pds.count() == len(s)
    for x in s:
        assert x in pds


def test_metric_picker_shows_form_pick_public_metrics(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = tools.make_samples_metrics()

    c = Client()
    assert c.login(username=d.username, password=d.password)
    q = query('wizard:challenge:metric.pick', c=c, kwargs={'pk': pk})

    s = q.html.select_one('.pick .public form select')
    options = s.select('option')
    options_txt = [x.text for x in options]

    assert len(options) == len(samples)
    for s in samples:
        assert s.name in options_txt


def test_metric_picker_when_select_public_metric_returns_to_metric_update(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = tools.make_samples_metrics()
    s = samples[0]

    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:metric.pick', kwargs={'pk': pk}),
               {'kind': 'public', 'metric': s.pk})

    assert_redirects(r, reverse('wizard:challenge:metric', kwargs={'pk': pk}))


def test_metric_picker_once_selected_redirects_to_update_metric(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc

    samples = tools.make_samples_metrics()
    s = samples[0]

    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.post(reverse('wizard:challenge:metric.pick', kwargs={'pk': pk}),
               {'kind': 'public', 'metric': s.pk})

    r = c.get(reverse('wizard:challenge:metric.pick', kwargs={'pk': pk}))
    assert_redirects(r, reverse('wizard:challenge:metric', kwargs={'pk': pk}))
