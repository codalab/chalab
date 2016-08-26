from collections import namedtuple

import pytest
from django.test import Client

from tests.tools import make_request, random_user_descr, html, register
from tests.wizard.tools import make_challenge
from wizard import views as wizard_views

ChallengeTuple = namedtuple('ChallengeTuple', ['user', 'challenge', 'response', 'html'])
UserTuple = namedtuple('UserTuple', ['client', 'desc', 'registration', 'user'])


@pytest.fixture(scope='function')
def random_user():
    c = Client()
    desc = random_user_descr('richard_f')
    r = register(c, desc)

    return UserTuple(client=c, desc=desc, registration=r, user=r.context['user'])


@pytest.fixture(scope='function')
def random_challenge():
    """Return the challenge and corresponding view"""
    request = make_request('/', user=random_user_descr('john_doe'))
    c = make_challenge(user=request.user)
    resp = wizard_views.ChallengeDescriptionDetail.as_view()(request, pk=c.pk)
    h = html(resp)

    return ChallengeTuple(user=request.user, challenge=c, response=resp, html=h)
