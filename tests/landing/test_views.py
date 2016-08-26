import pytest
from django.core.urlresolvers import resolve

from landing.views import home, about
from ..tools import q

pytestmark = pytest.mark.django_db
NAV_ANONYMOUS = ['home', 'about', 'signup', 'login']


class TestHomePage:
    def test_root_url_resolves_to_home_view(self):
        found = resolve('/')
        assert found.func == home

    def test_shows_header_logo(self):
        html = q(home)
        assert html.select('header #logo')[0] is not None

    def test_header_logo_points_to_root(self):
        html = q(home)
        l = html.select('header #logo a')[0]
        assert l['href'] == '/'

    def test_is_polite(self):
        html = q(home)
        assert 'Welcome to' in html.select('.hero h1')[0].string

    def test_shows_hero(self):
        html = q(home)
        assert html.select('.hero .lead')[0] is not None

    def test_shows_nav(self):
        html = q(home)

        assert html.select('nav')[0] is not None

    def test_nav_contains_links(self):
        html = q(home)

        ids = [x['id'] for x in html.select('nav li')]

        assert NAV_ANONYMOUS == ids

    def test_nav_about_points_to_about_page(self):
        html = q(home)
        about = html.select('nav li#about a')[0]
        assert about['href'] == '/about'

    def test_nav_home_points_to_home_page(self):
        html = q(home)
        about = html.select('nav li#home a')[0]
        assert about['href'] == '/'


class TestAboutPage:
    def test_about_url_resolves_to_about_view(self):
        found = resolve('/about')
        assert found.func == about

    def test_about_contains_nav(self):
        html = q(about)

        n = html.select('nav li a')
        assert len(n) == len(NAV_ANONYMOUS)

    def test_about_shows_infos(self):
        html = q(about)

        t = html.select('.content h1')[0]
        assert t.text == 'About'

        t = html.select('.content')[0]
        assert len(t.text) > 100
