from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase

from ..tools import last_mail, register, random_user


class AuthTest(TestCase):
    def test_register_goes_to_wizard_home(self):
        r = register(Client(), random_user('john_doe'))

        self.assertRedirects(r, reverse('wizard:home'))

    def test_register_send_activation_mail(self):
        register(Client(), random_user('john_doe'))

        self.assertIsNotNone(last_mail())
        self.assertIn('activate', last_mail().body)

    def test_register_then_home_redirects_to_wizard(self):
        c = Client()
        register(c, random_user('john_doe'))

        r = c.get('/')

        self.assertRedirects(r, reverse('wizard:home'))
