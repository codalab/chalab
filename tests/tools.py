from bs4 import BeautifulSoup
from django.core import mail
from django.test import Client
from django.urls import reverse


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


def q2(f, c=None):
    c = c or Client()
    r = c.get(reverse(f))
    html = BeautifulSoup(r.content, 'html.parser')
    return r, html


def q(f, c=None):
    _, html = q2(f, c=c)
    return html
