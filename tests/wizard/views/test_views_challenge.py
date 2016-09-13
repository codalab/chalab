import pytest
from django.urls import reverse

from tests.tools import query, assert_redirects, sreverse
from wizard import models

pytestmark = pytest.mark.django_db


class TestCreateChallenge(object):
    def test_shows_challenge_form(self, random_user):
        q = query('wizard:create', random_user.client)
        assert 'form' in q.response.context

    def test_shows_panel_create(self, random_user):
        q = query('wizard:create', random_user.client)
        assert q.html.select('.panel')[0]['id'], 'create-challenge'

    def test_redirect_to_challenge(self, random_user):
        client, user = random_user.client, random_user.user

        r = client.post(reverse('wizard:create'),
                        {'title': 'A challenge',
                         'organization_name': 'an organization',
                         'description': 'the description'})

        last_challenge = models.ChallengeModel.objects.filter(created_by=user).last()
        assert_redirects(r, reverse('wizard:challenge', kwargs={'pk': last_challenge.pk}))


class TestChallengePage(object):
    @pytest.mark.parametrize("flow_name", [
        'data', 'task', 'metric', 'protocol', 'documentation'
    ])
    def test_shows_flow_links(self, flow_name, random_challenge):
        c, h = random_challenge.challenge, random_challenge.html

        flow_selector = '.flow-full .step.%s a' % flow_name
        page_name = 'wizard:challenge:%s' % flow_name

        assert (h.select(flow_selector)[0]['href'] == sreverse(page_name, pk=c.pk))

    def test_shows_edit_button(self, cb):
        r = cb.get('wizard:challenge', pk=cb.pk)

        link = r.html.select_one('.jumbotron a.btn-edit')
        assert link['href'] == sreverse('wizard:challenge:edit', pk=cb.pk)


class TestChallengeEditPage(object):
    def test_provides_form(self, cb):
        r = cb.get('wizard:challenge:edit', pk=cb.pk)
        assert 'form' in r.context

    def test_uses_challenge(self, cb):
        r = cb.get('wizard:challenge:edit', pk=cb.pk)
        assert r.context['form'].initial['title'] == cb.challenge.title

    def test_on_post_moves_back_to_challenge(self, cb):
        c = cb.challenge
        r = cb.post('wizard:challenge:edit', pk=cb.pk,
                    data=dict(title=c.title, organization_name=c.organization_name,
                              description=c.description))

        assert_redirects(r, sreverse('wizard:challenge', pk=cb.pk))

    def test_on_rename_update_model(self, cb):
        c = cb.challenge
        new_title = c.title + '- renamed'

        cb.post('wizard:challenge:edit', data={
            'title': new_title,
            'organization_name': c.organization_name,
            'description': c.description}, pk=cb.pk)

        c.refresh_from_db()
        assert cb.challenge.title == new_title
