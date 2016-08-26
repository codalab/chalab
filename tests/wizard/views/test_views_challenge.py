import pytest
from django.urls import reverse

from tests.tools import query, assert_redirects
from wizard import models

pytestmark = pytest.mark.django_db


def test_create_challenge_shows_challenge_form(random_user):
    q = query('wizard:create', random_user.client)
    assert 'form' in q.response.context


def test_create_challenges_shows_panel_create(random_user):
    q = query('wizard:create', random_user.client)
    assert q.html.select('.panel')[0]['id'], 'create-challenge'


def test_create_challenges_redirect_to_challenge(random_user):
    client, user = random_user.client, random_user.user

    r = client.post(reverse('wizard:create'),
                    {'title': 'A challenge',
                     'organization_name': 'an organization',
                     'description': 'the description'})

    last_challenge = models.ChallengeModel.objects.filter(created_by=user).last()
    assert_redirects(r, reverse('wizard:challenge', kwargs={'pk': last_challenge.pk}))


@pytest.mark.parametrize("flow_name", [
    'data', 'task', 'metric', 'protocol', 'baseline', 'documentation', 'rules'
])
def test_challenge_page_shows_flow_links(flow_name, random_challenge):
    c, h = random_challenge.challenge, random_challenge.html

    flow_selector = '.flow-full .step.%s a' % flow_name
    page_name = 'wizard:%s' % flow_name

    assert (h.select(flow_selector)[0]['href'] == reverse(page_name, kwargs=dict(pk=c.pk)))
