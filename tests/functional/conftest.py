import pytest

from tests import selen
from tests.tools import random_user_desc, random_challenge_desc
from .pages import HomePage


@pytest.fixture(scope='function')
def raw_driver():
    d = selen.raw_driver()
    try:
        yield d
    finally:
        d.close()


@pytest.fixture(scope='function')
def home(raw_driver):
    raw_driver.get(selen.LIVE_SERVER_URL)
    return HomePage(raw_driver)


@pytest.fixture(scope='function')
def wizard(home):
    u = random_user_desc('napier_j')
    p = home.signup()

    p = p.register(u)
    assert p.is_app('wizard')
    return p


@pytest.fixture(scope='function')
def challenge(wizard):
    c = random_challenge_desc('some challenge')
    p = wizard.create_challenge()
    p = p.submit(c)
    assert p.is_('wizard', 'challenge')
    return p
