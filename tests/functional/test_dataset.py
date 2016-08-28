from django.test import LiveServerTestCase

from .. import selen
from .pages import Page
from ..tools import random_user_desc


class TestDataset(LiveServerTestCase):
    def setUp(self):
        self._driver = selen.raw_driver()
        super().setUp()

    def tearDown(self):
        self._driver.close()
        super().tearDown()

