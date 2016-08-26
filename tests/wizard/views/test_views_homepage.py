import pytest
from django.test import Client
from django.urls import reverse

from tests.tools import q, assert_redirects
from wizard import models

pytestmark = pytest.mark.django_db
NAV_LOGGED = ['home', 'about', 'login']


def test_after_login_returns_200(random_user):
    r = random_user.client.get(reverse('wizard:home'))
    assert r.status_code == 200


def test_without_login_returns_403():
    r = Client().get(reverse('wizard:home'))

    assert_redirects(r, '/accounts/login/?next=/wizard/')


def test_after_login_is_app_wizard(random_user):
    home = q('wizard:home', random_user.client)
    app = home.select('.app')

    assert len(app) == 1
    assert app[0]['id'] == 'wizard'


def test_after_login_shows_empty_list_of_challenges(random_user):
    home = q('wizard:home', random_user.client)

    challenges_block = home.select('.challenges')
    challenges = home.select('.challenges .challenge')
    assert len(challenges_block) == 1
    assert len(challenges) == 0


def test_shows_create_challenge_button(random_user):
    home = q('wizard:home', random_user.client)

    create_btn = home.select('a.create-challenge')[0]
    assert create_btn['href'] == reverse('wizard:create')


def test_challenge_is_in_context(random_user):
    m = models.ChallengeModel.objects.create(title='a challenge',
                                             organization_name='the organization',
                                             description='the description',
                                             created_by=random_user.user)

    r = random_user.client.get(reverse('wizard:home'))

    assert r.context['object_list'].count() == 1
    assert r.context['object_list'].first() == m


def test_challenge_is_in_html(random_user):
    models.ChallengeModel.objects.create(title='a challenge',
                                         organization_name='the organization',
                                         description='the description',
                                         created_by=random_user.user)

    html = q('wizard:home', random_user.client)
    challenges = html.select('.challenges .challenge')

    assert len(challenges) == 1
