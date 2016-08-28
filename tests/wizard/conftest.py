from collections import namedtuple

import pytest
from django.test import Client

from tests.tools import make_request, random_user_desc, html, register, make_user
from tests.wizard.models.tools import make_challenge
from wizard import views as wizard_views

ChallengeTuple = namedtuple('ChallengeTuple', ['user', 'desc', 'challenge', 'response', 'html'])
UserTuple = namedtuple('UserTuple', ['client', 'desc', 'registration', 'user'])


@pytest.fixture(scope='function')
def random_user():
    c = Client()
    desc = random_user_desc('richard_f')
    r = register(c, desc)

    return UserTuple(client=c, desc=desc, registration=r, user=r.context['user'])


@pytest.fixture(scope='function')
def random_challenge():
    """Return the challenge and corresponding view"""
    desc = random_user_desc('john_doe')
    user = make_user(desc)
    request = make_request('/', user=user)

    chall = make_challenge(user=request.user)
    resp = wizard_views.ChallengeDescriptionDetail.as_view()(request, pk=chall.pk)
    h = html(resp)

    return ChallengeTuple(user=request.user, desc=desc, challenge=chall, response=resp, html=h)
