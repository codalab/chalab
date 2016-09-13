import pytest
from django.urls import reverse

from tests.tools import make_request, assert_redirects, html, sreverse
from tests.wizard.models.tools import make_samples_datasets
from wizard import views as wiz

pytestmark = pytest.mark.django_db


def test_open_data_redirects_to_picker(random_challenge):
    pk = random_challenge.challenge.pk
    url = reverse('wizard:challenge:data', kwargs={'pk': random_challenge.challenge.pk})
    request = make_request(url, user=random_challenge.user)

    response = wiz.ChallengeDataEdit.as_view()(request, pk=pk)

    assert_redirects(response, reverse('wizard:challenge:data.pick', kwargs={'pk': pk}),
                     fetch_redirect_response=False)


class TestDataPicker(object):
    def test_shows_public_dataset(self, random_challenge):
        pk = random_challenge.challenge.pk

        url = reverse('wizard:challenge:data.pick', kwargs={'pk': random_challenge.challenge.pk})
        request = make_request(url, user=random_challenge.user)

        response = wiz.data_picker(request, pk=pk)
        h = html(response)

        assert h.select_one('.module')['id'] == 'picker'
        assert 'Pick' in h.select_one('.module h3').text

    def test_shows_public_datasets_empty(self, cb):
        r = cb.get('wizard:challenge:data.pick', pk=cb.pk)
        assert r.context['public_datasets'].count() == 0

    def test_shows_public_datasets_with_a_couple(self, cb):
        (d1, d2) = make_samples_datasets()

        r = cb.get('wizard:challenge:data.pick', pk=cb.pk)
        pds = r.context['public_datasets']

        assert pds.count() == 2
        assert d1 in pds
        assert d2 in pds

    def test_shows_form_pick_public_datasets(self, cb):
        samples = make_samples_datasets()

        r = cb.get('wizard:challenge:data.pick', pk=cb.pk)

        s = r.html.select_one('.pick .public form select')
        options = s.select('option')
        options_txt = [x.text for x in options]

        assert len(options) == len(samples)
        for s in samples:
            assert s.name in options_txt

    def test_when_select_public_dataset_returns_to_regular_data(self, cb):
        samples = make_samples_datasets()
        s = samples[0]

        r = cb.post('wizard:challenge:data.pick', pk=cb.pk,
                    data={'kind': 'public', 'dataset': s.pk})
        assert_redirects(r, sreverse('wizard:challenge:data', pk=cb.pk))

    def test_once_selected_redirects_to_regular_data(self, cb):
        samples = make_samples_datasets()
        s = samples[0]

        cb.post('wizard:challenge:data.pick', pk=cb.pk,
                data={'kind': 'public', 'dataset': s.pk})

        r = cb.get('wizard:challenge:data.pick', pk=cb.pk)
        assert_redirects(r, sreverse('wizard:challenge:data', pk=cb.pk))
