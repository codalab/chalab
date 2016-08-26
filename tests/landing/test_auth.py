import pytest
from django.core.urlresolvers import reverse
from django.test import Client

from tests.tools import last_mail, register, random_user_descr, assert_redirects

pytestmark = pytest.mark.django_db


class TestAuth:
    def test_register_goes_to_wizard_home(self):
        r = register(Client(), random_user_descr('john_doe'))

        assert_redirects(r, reverse('wizard:home'))

    def test_register_send_activation_mail(self):
        register(Client(), random_user_descr('john_doe'))

        assert last_mail() is not None
        assert 'activate' in last_mail().body

    def test_register_then_home_redirects_to_wizard(self):
        c = Client()
        register(c, random_user_descr('john_doe'))

        r = c.get('/')

        assert_redirects(r, reverse('wizard:home'))
