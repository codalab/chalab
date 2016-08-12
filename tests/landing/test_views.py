from bs4 import BeautifulSoup
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.test import TestCase

from landing.views import home, about

NAV_ANONYMOUS = ['home', 'about', 'signup', 'login']


def r(f):
    request = HttpRequest()
    response = f(request)
    html = BeautifulSoup(response.content, 'html.parser')
    return html


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_shows_header_logo(self):
        html = r(home)
        assert html.select('header #logo')[0] is not None

    def test_header_logo_points_to_root(self):
        html = r(home)
        l = html.select('header #logo a')[0]
        assert l['href'] == '/'

    def test_shows_register_form(self):
        html = r(home)
        f = html.select('.register form')
        assert f[0] is not None

    def test_is_polite(self):
        html = r(home)
        assert 'Welcome to' in html.select('h1')[0].string

    def test_shows_hero(self):
        html = r(home)
        assert html.select('.hero .details')[0] is not None

    def test_shows_nav(self):
        html = r(home)

        assert html.select('.nav')[0] is not None

    def test_nav_contains_links(self):
        html = r(home)

        ids = [x['id'] for x in html.select('.nav li')]

        self.assertEqual(NAV_ANONYMOUS, ids)

    def test_nav_about_points_to_about_page(self):
        html = r(home)
        about = html.select('.nav li#about a')[0]
        assert about['href'] == '/about'

    def test_nav_home_points_to_home_page(self):
        html = r(home)
        about = html.select('.nav li#home a')[0]
        assert about['href'] == '/'


class AboutPageTest(TestCase):
    def test_about_url_resolves_to_about_view(self):
        found = resolve('/about')
        self.assertEqual(found.func, about)

    def test_about_contains_nav(self):
        html = r(about)

        n = html.select('.nav li a')
        self.assertEqual(len(n), len(NAV_ANONYMOUS))

    def test_about_shows_infos(self):
        html = r(about)

        t = html.select('.content h1')[0]
        assert t.text == 'About'

        t = html.select('.content')[0]
        assert len(t.text) > 100
