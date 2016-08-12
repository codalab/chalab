from django.test import Client
from django.test import TestCase
from django.urls import reverse

from wizard import views
from ..tools import register

NAV_LOGGED = ['home', 'about', 'login']


class HomePageTest(TestCase):
    def test_home_after_login_returns_200(self):
        c, _ = register('richard_f')
        r = c.get(reverse(views.home))
        self.assertEqual(r.status_code, 200)

    def test_home_without_login_returns_403(self):
        r = Client().get(reverse(views.home))

        self.assertRedirects(r, '/accounts/login/?next=/home')
