from django.core.urlresolvers import reverse
from django.test import TestCase

from ..tools import last_mail, register


class AuthTest(TestCase):
    def test_register_goes_to_wizard_home(self):
        c, r = register('john_doe')

        self.assertRedirects(r, reverse('wizard:home'))
        self.assertIsNotNone(last_mail())
        self.assertIn('activate', last_mail().body)

    def test_register_then_home_redirects_to_please_activate(self):
        c, _ = register('isaac_doe')
        r = c.get('/')

        self.assertRedirects(r, reverse('wizard:home'))
