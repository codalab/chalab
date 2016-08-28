from django.test import LiveServerTestCase

from .pages import Page
from .. import selen
from ..tools import random_user_desc


class BasicTest(LiveServerTestCase):
    def setUp(self):
        self._driver = selen.raw_driver()
        super(BasicTest, self).setUp()

    def tearDown(self):
        self._driver.close()
        super(BasicTest, self).tearDown()

    def test_is_setup(self):
        p = Page(self._driver).get(selen.LIVE_SERVER_URL)
        assert 'Welcome to' in p.by_css('.hero h1').text

    def test_browse_around_shows_the_basics(self):
        p = Page(self._driver).get(selen.LIVE_SERVER_URL)

        # The home page show a welcome and some explanations
        assert 'Welcome to' in p.by_css('.hero h1').text
        assert len(p.by_css('.hero .lead').text) > 10

        # I can click on the About page, It shows more information
        p = p.nav_to('about')
        assert len(p.by_css('.content').text) > 100

        # I can go back home with the logo in header
        p = p.click_on_logo()

        # I can open the registration
        p = p.nav_to('signup')

        # It shows a registration form
        f = p.form('.signup')

        assert f.has_fields(inputs=['username', 'email', 'password1', 'password2'])

    def test_register_and_create_first_competition(self):
        u = random_user_desc('napier_j')
        p = Page(self._driver).get(selen.LIVE_SERVER_URL)

        # There's a register button in the navigation
        p = p.nav_to('signup')

        # I can fill the registration form
        f = p.form('.signup')
        f.fill(username=u.username, email=u.email,
               password1=u.password, password2=u.password).submit()

        # I'm on the wizard home page
        assert p.is_app('wizard')
        assert len(p.challenges) == 0

        # I can create a challenge
        p = p.click('.create-challenge')
        assert p.is_app('wizard', 'create-challenge')

        # I can fill the form
        f = p.form('.challenge')

        # TODO(laurent): Upload organization image
        f.fill(title='My first competition',
               organization_name='UmbrellaCorp',
               description='Cure Zombiism').submit()

        assert p.is_app('wizard', 'challenge')

        # I can go back home and find my competition
        p = p.get(selen.LIVE_SERVER_URL)

        assert len(p.challenges) == 1
        assert p.challenges[0].title == 'My first competition'
