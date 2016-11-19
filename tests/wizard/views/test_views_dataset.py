import pytest
from django.urls import reverse

from tests.tools import make_request, assert_redirects, html, sreverse
from tests.wizard.models.tools import make_samples_datasets
from wizard import models
from wizard import views as wiz

pytestmark = pytest.mark.django_db


class TestDataPicker(object):
    def test_shows_public_dataset(self, random_challenge):
        pk = random_challenge.challenge.pk

        url = reverse('wizard:challenge:data.pick', kwargs={'pk': random_challenge.challenge.pk})
        request = make_request(url, user=random_challenge.user)

        response = wiz.data_picker(request, pk=pk)
        h = html(response)

        assert h.select_one('.module')['id'] == 'picker'
        assert 'Public' in h.select_one('.module .pick h4').text

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

    def test_once_picked_returning_to_picker_allows_you_to_pick_another(self, cb_and_public_data):
        samples = make_samples_datasets()
        s = samples[-1]

        assert s != cb_and_public_data.sample

        r = cb_and_public_data.post('wizard:challenge:data.pick', pk=cb_and_public_data.pk,
                                    data={'kind': 'public', 'dataset': s.pk})

        assert_redirects(r, sreverse('wizard:challenge:data', pk=cb_and_public_data.pk))


class TestDataCreator:
    def test_when_create_dataset_returns_to_regular_data(self, cb):
        r = cb.post('wizard:challenge:data.pick', pk=cb.pk,
                    data={'kind': 'create', 'name': 'some dataset'})
        assert_redirects(r, sreverse('wizard:challenge:data', pk=cb.pk))

    def test_when_create_it_adds_the_dataset_name(self, cb):
        cb.post('wizard:challenge:data.pick', pk=cb.pk,
                data={'kind': 'create', 'name': 'some dataset'})

        assert models.DatasetModel.objects.filter(name='some dataset').count() == 1

    def test_when_create_it_sets_the_dataset_for_challenge(self, cb):
        cb.post('wizard:challenge:data.pick', pk=cb.pk,
                data={'kind': 'create', 'name': 'another magic dataset'})

        assert models.ChallengeModel.get(cb.pk).dataset.name == 'another magic dataset'


class TestDataUpdate(object):
    def test_open_data_redirects_to_picker(self, random_challenge):
        pk = random_challenge.challenge.pk
        url = reverse('wizard:challenge:data', kwargs={'pk': random_challenge.challenge.pk})
        request = make_request(url, user=random_challenge.user)

        response = wiz.ChallengeDataEdit.as_view()(request, pk=pk)

        assert_redirects(response, reverse('wizard:challenge:data.pick', kwargs={'pk': pk}),
                         fetch_redirect_response=False)

    def test_cant_change_fields_for_public_datasets_i_dont_own_form(self, cb_and_public_data):
        r = cb_and_public_data.get('wizard:challenge:data', pk=cb_and_public_data.pk)
        assert 'disabled' in r.lhtml.cssselect('form #id_name')[0].attrib

    def test_cant_update_public_datasets_i_dont_own_form(self, cb_and_public_data):
        r = cb_and_public_data.get('wizard:challenge:data', pk=cb_and_public_data.pk)
        assert 'disabled' in r.lhtml.cssselect('form button[type="submit"]')[0].attrib

    def test_cant_update_public_ds_i_dont_own_post(self, cb_and_public_data):
        s = cb_and_public_data.sample
        old_name = s.name

        r = cb_and_public_data.post('wizard:challenge:data', pk=cb_and_public_data.pk,
                                    data={'title': 'something new'})
        assert r.status_code == 400

        s.refresh_from_db()
        assert s.name == old_name

    def test_can_update_datasets_i_own_form(self, cb_and_my_data):
        r = cb_and_my_data.get('wizard:challenge:data', pk=cb_and_my_data.pk)
        assert 'disabled' not in r.lhtml.cssselect('form button[type="submit"]')[0].attrib

    def test_editor_page_shows_upload_automl_button(self, cb_and_my_data):
        r = cb_and_my_data.get('wizard:challenge:data', pk=cb_and_my_data.pk)

        uploader = r.lhtml.cssselect('input[type="file"]#id_automl_upload')[0]
        assert uploader is not None

    def test_editor_page_can_upload_automl(self, cb_and_my_data):
        with open('tests/wizard/resources/uploadable/automl_dataset.zip', 'rb') as fp:
            r = cb_and_my_data.post('wizard:challenge:data', pk=cb_and_my_data.pk,
                                    data={
                                        'name': 'updated dataset',
                                        'automl_upload': fp
                                    })
        assert r.status_code == 302

    def test_editor_page_can_upload_automl_sets_dataset_ready(self, cb_and_my_data):
        with open('tests/wizard/resources/uploadable/automl_dataset.zip', 'rb') as fp:
            r = cb_and_my_data.post('wizard:challenge:data', pk=cb_and_my_data.pk,
                                    data={
                                        'name': 'updated dataset',
                                        'automl_upload': fp
                                    })
        c = cb_and_my_data.challenge
        c.refresh_from_db()
        ds = c.dataset
        assert ds.is_ready

    def test_dataset_page_shows_picker_button(self, cb_and_public_data):
        r = cb_and_public_data.get('wizard:challenge:data', pk=cb_and_public_data.pk)

        picker = r.lhtml.cssselect('.btn.picker')[0]

        assert picker is not None
        assert picker.attrib['href'] == sreverse('wizard:challenge:data.pick',
                                                 pk=cb_and_public_data.pk)

    def test_dataset_page_shows_ready_ok_for_public(self, cb_and_public_data):
        r = cb_and_public_data.get('wizard:challenge:data', pk=cb_and_public_data.pk)

        status = r.lhtml.cssselect('.status.ready')[0]
        assert status is not None

    def test_dataset_page_shows_not_ready_for_my_just_created(self, cb_and_my_data):
        r = cb_and_my_data.get('wizard:challenge:data', pk=cb_and_my_data.pk)

        status = r.lhtml.cssselect('.status.not-ready')[0]
        assert status is not None

    def test_once_picked_picking_another_update_page(self, cb_and_public_data):
        samples = make_samples_datasets()
        s = samples[-1]

        assert s != cb_and_public_data.sample

        cb_and_public_data.post('wizard:challenge:data.pick', pk=cb_and_public_data.pk,
                                data={'kind': 'public', 'dataset': s.pk})

        r = cb_and_public_data.get('wizard:challenge:data', pk=cb_and_public_data.pk)

        context = r.context

        assert 'form' in context
        assert context['form'].initial['name'] == s.name
