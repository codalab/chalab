from bs4 import BeautifulSoup
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.test import TestCase

from landing.views import welcome


class HomePageTest(TestCase):
    def test_root_url_resolves_to_welcome_view(self):
        found = resolve('/')
        self.assertEqual(found.func, welcome)

    def test_welcome_is_polite(self):
        request = HttpRequest()
        response = welcome(request)
        html = BeautifulSoup(response.content, 'html.parser')

        assert 'Welcome to' in html.find('h1').string
