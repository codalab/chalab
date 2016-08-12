from django.test import LiveServerTestCase

import tests.selen as selen


class BasicTest(LiveServerTestCase):
    def setUp(self):
        self._driver = selen.raw_driver()
        super(BasicTest, self).setUp()

    def tearDown(self):
        self._driver.close()
        super(BasicTest, self).tearDown()

    def test_is_setup(self):
        self._driver.get(selen.LIVE_SERVER_URL)

        e = self._driver.find_element_by_css_selector('.hero h1')
        assert 'Welcome to' in e.text
