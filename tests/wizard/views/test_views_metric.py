import pytest
from django.urls import reverse

from tests.tools import make_request, assert_redirects, html, sreverse
from tests.wizard.models import tools
from wizard import views as wiz

pytestmark = pytest.mark.django_db


def test_open_metric_redirects_to_picker(cb):
    r = cb.get('wizard:challenge:metric', pk=cb.pk)
    assert_redirects(r, sreverse('wizard:challenge:metric.pick', pk=cb.pk))


def test_metric_picker_shows_public_metrics_picker_ui(random_challenge):
    pk = random_challenge.challenge.pk

    url = reverse('wizard:challenge:metric.pick', kwargs={'pk': pk})
    request = make_request(url, user=random_challenge.user)

    response = wiz.metric_picker(request, pk=pk)
    h = html(response)

    assert h.select_one('.module')['id'] == 'picker'
    assert 'Which metric' in h.select_one('.module h3').text


class TestMetricPicker(object):
    def test_has_public_metric_in_context(self, cb):
        s = tools.make_samples_metrics()

        r = cb.get('wizard:challenge:metric.pick', pk=cb.pk)
        pds = r.context['public_metrics']

        assert pds.count() == len(s)
        for x in s:
            assert x in pds

    def test_shows_form_pick_public_metrics(self, cb):
        samples = tools.make_samples_metrics()

        r = cb.get('wizard:challenge:metric.pick', pk=cb.pk)

        s = r.html.select_one('.pick .public form select')
        options = s.select('option')
        options_txt = [x.text for x in options]

        assert len(options) == len(samples)
        for s in samples:
            assert s.name in options_txt

    def test_when_select_public_metric_returns_to_metric_update(self, cb):
        samples = tools.make_samples_metrics()
        s = samples[0]

        r = cb.post('wizard:challenge:metric.pick', pk=cb.pk,
                    data={'kind': 'public', 'metric': s.pk})

        assert_redirects(r, sreverse('wizard:challenge:metric', pk=cb.pk))

    def test_once_selected_redirects_to_update_metric(self, cb):
        samples = tools.make_samples_metrics()
        s = samples[0]

        cb.post('wizard:challenge:metric.pick', pk=cb.pk,
                data={'kind': 'public', 'metric': s.pk})

        r = cb.get('wizard:challenge:metric.pick', pk=cb.pk)
        assert_redirects(r, sreverse('wizard:challenge:metric', pk=cb.pk))


@pytest.fixture(scope='function')
def cbpicked(cb):
    samples = tools.make_samples_metrics()
    s = samples[0]

    cb.post('wizard:challenge:metric.pick', pk=cb.pk,
            data={'kind': 'public', 'metric': s.pk})

    cb.metric = s
    yield cb


class TestMetricUpdate(object):
    def test_edit_form_is_disabled_for_public_metrics(self, cbpicked):
        r = cbpicked.get('wizard:challenge:metric', pk=cbpicked.pk)
        assert 'disabled' in r.lhtml.cssselect('form #id_name')[0].attrib

    def test_cant_update_public_metrics_on_post(self, cbpicked):
        s = cbpicked.metric
        old_name = s.name

        r = cbpicked.post('wizard:challenge:metric', pk=cbpicked.pk,
                          data={'title': 'something new'})

        assert r.status_code == 400

        s.refresh_from_db()
        assert s.name == old_name
