import pytest

from .pages import HomePage
from .. import selen
from ..tools import random_user_desc


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


def test_is_setup(home):
    assert 'Welcome to' in home.hero.h1.text


def test_browse_around_shows_the_basics(home):
    # The home page show a welcome and some explanations
    assert 'Welcome to' in home.hero.h1.text
    assert len(home.hero.lead.text) > 10

    # I can click on the About page, It shows more information
    p = home.about()
    assert len(p.content.text) > 100

    # I can go back home with the logo in header
    p = p.click_logo()

    # I can open the registration
    p = p.signup()

    # It shows a registration form
    f = p.form

    assert f.has_fields(inputs=['username', 'email', 'password1', 'password2'])


def test_register_and_create_first_competition(home):
    u = random_user_desc('napier_j')

    # There's a register button in the navigation
    p = home.signup()

    # I can fill the registration form
    p = p.register(username=u.username, email=u.email, password=u.password)

    # I'm on the wizard home page
    assert p.is_app('wizard')
    assert len(p.challenges) == 0

    # I can create a challenge
    p = p.create_challenge()
    assert p.is_app('wizard', 'create-challenge')

    # I can fill the form
    # TODO(laurent): Upload organization image
    p.submit(title='My first competition',
             org_name='UmbrellaCorp',
             description='Cure Zombiism')

    assert p.is_app('wizard', 'challenge')

    # I can go back home and find my competition
    p = p.go_home(selen.LIVE_SERVER_URL)

    assert len(p.challenges) == 1
    assert p.challenges[0].title == 'My first competition'
