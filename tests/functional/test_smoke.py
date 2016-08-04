from django.test import LiveServerTestCase

import tests.selen as selen

SELECTOR_HERO = '.hero'


class BasicTest(LiveServerTestCase):
    def setUp(self):
        self._driver = selen.raw_driver()
        super(BasicTest, self).setUp()

    def tearDown(self):
        self._driver.close()
        super(BasicTest, self).tearDown()

    def test_register(self):
        self._driver.get(selen.LIVE_SERVER_URL)

        e = self._driver.find_element_by_css_selector('h1')
        assert 'It worked!' in e.text
