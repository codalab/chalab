import random

from django.test import LiveServerTestCase
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import tests.selen as selen


def random_user(name):
    name = '%s.%010d' % (name, random.randint(0, 1000000000))

    return {'name': name,
            'email': '%s@chalab.test' % name,
            'password': 'sadhasdjasdqwdnasdbkj'}


class BasicTest(LiveServerTestCase):
    def setUp(self):
        self._driver = selen.raw_driver()
        super(BasicTest, self).setUp()

    def tearDown(self):
        self._driver.close()
        super(BasicTest, self).tearDown()

    def by_css(self, selector, on_missing=Exception):
        try:
            return self._driver.find_element_by_css_selector(selector)
        except (NoSuchElementException, TimeoutException) as e:
            if on_missing != Exception:
                return on_missing
            else:
                raise e

    def by_css_many(self, selector, on_missing=Exception):
        try:
            return self._driver.find_elements_by_css_selector(selector)
        except (NoSuchElementException, TimeoutException) as e:
            if on_missing != Exception:
                return on_missing
            else:
                raise e

    def test_is_setup(self):
        self._driver.get(selen.LIVE_SERVER_URL)

        e = self._driver.find_element_by_css_selector('.hero h1')
        assert 'Welcome to' in e.text

    def test_browse_around_shows_the_basics(self):
        self._driver.get(selen.LIVE_SERVER_URL)

        # The home page show a welcome
        t = self.by_css('.hero h1')
        assert 'Welcome to Chalab' in t.text

        # And some explanations
        d = self.by_css('.hero .lead')
        assert len(d.text) > 10

        # I can click on the About page
        self.by_css('nav #about a').click()

        # It shows more information
        c = self.by_css('.content')
        assert len(c.text) > 100

        # I can go back home with the logo in header
        self.by_css('header #logo a').click()

        # I can open the registration
        self.by_css('nav #signup a').click()

        # It shows a registration form
        f = self.by_css('form.signup')
        assert f.find_element_by_css_selector('input#id_username') is not None
        assert f.find_element_by_css_selector('input#id_email') is not None
        assert f.find_element_by_css_selector('input#id_password1') is not None
        assert f.find_element_by_css_selector('input#id_password2') is not None

    def test_register_and_create_first_competition(self):
        self._driver.get(selen.LIVE_SERVER_URL)

        # There's a register button in the navigation
        self.by_css('nav #signup a').click()

        # I can fill the registration form
        f = self.by_css('form.signup')

        u = random_user('napier_j')

        f.find_element_by_css_selector('input#id_username').send_keys(u['name'])
        f.find_element_by_css_selector('input#id_email').send_keys(u['email'])
        f.find_element_by_css_selector('input#id_password1').send_keys(u['password'])
        f.find_element_by_css_selector('input#id_password2').send_keys(u['password'])

        f.submit()

        # I'm on the wizard home page
        assert self.by_css('.app#wizard') is not None
        assert self.by_css('.challenges') is not None
        assert self.by_css_many('.challenges .challenge', on_missing=[]) == []

        # I can create a challenge
        self.by_css('.create-challenge').click()

        self._driver.save_screenshot('nope.png')

        assert self.by_css('.app#wizard')
        assert self.by_css('.panel#create-challenge')

        # I can fill the form
        f = self.by_css('form.challenge')

        f.find_element_by_css_selector('input#id_title').send_keys('My first competition')
        f.find_element_by_css_selector('input#id_organization_name').send_keys('UmbrellaCorp')
        # TODO(laurent): Upload organization image
        f.find_element_by_css_selector('textarea#id_description').send_keys('Cure Zombiism.')

        f.submit()

        assert self.by_css('.panel#challenge')

        # I can go back home and find my competition
        self._driver.get(selen.LIVE_SERVER_URL)

        cs = self.by_css_many('.challenges .challenge', on_missing=[])
        assert len(cs) == 1
        assert cs[0].find_element_by_css_selector('.title').text == 'My first competition'
