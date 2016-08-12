from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase


def last_mail():
    return mail.outbox[-1]


def register(username, email=None, password='1q2w3e4r5t6y7u8i9o0'):
    if email is None:
        email = '%s@test.test' % username

    c = Client()
    r = c.post(reverse('account_signup'),
               {'username': username, 'email': email,
                'password1': password, 'password2': password})
    return c, r


class AuthTest(TestCase):
    def test_register_goes_to_wizard_home(self):
        c, r = register('john_doe')

        self.assertRedirects(r, reverse('wizard.home'))
        self.assertIsNotNone(last_mail())
        self.assertIn('activate', last_mail().body)

    def test_register_then_home_redirects_to_please_activate(self):
        c, _ = register('isaac_doe')
        r = c.get('/')

        self.assertRedirects(r, reverse('wizard.home'))
