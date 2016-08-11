from django.test import LiveServerTestCase

import tests.selen as selen


class BasicTest(LiveServerTestCase):
    def setUp(self):
        self._driver = selen.raw_driver()
        super(BasicTest, self).setUp()

    def tearDown(self):
        self._driver.close()
        super(BasicTest, self).tearDown()

    def by_css(self, selector):
        return self._driver.find_element_by_css_selector(selector)

    def test_browse_around_shows_the_basics(self):
        self._driver.get(selen.LIVE_SERVER_URL)

        # The home page show a welcome
        t = self.by_css('.hero h1')
        assert 'Welcome to Chalab' in t.text

        # And some explanations
        d = self.by_css('.hero .details')
        assert len(d.text) > 10

        # I can click on the About page
        self.by_css('.nav #about a').click()

        # It shows more information
        c = self.by_css('.content')
        assert len(c.text) > 100

        # I can go back home and see the register
        self.by_css('header #logo a').click()

        # It shows a registration form
        f = self.by_css('.register form')
        assert f.find_element_by_css_selector('.email input') is not None
        assert f.find_element_by_css_selector('.password input') is not None
        assert f.find_element_by_css_selector('.password_bis input') is not None

    def test_is_setup(self):
        self._driver.get(selen.LIVE_SERVER_URL)

        e = self._driver.find_element_by_css_selector('h1')
        assert 'Welcome to' in e.text
