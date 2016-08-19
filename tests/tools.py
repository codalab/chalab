import random
from collections import namedtuple

from bs4 import BeautifulSoup
from django.core import mail
from django.test import Client
from django.urls import reverse

UserTuple = namedtuple('UserTuple', ['name', 'email', 'password'])


def last_mail():
    return mail.outbox[-1]


def random_user(name):
    name = '%s.%010d' % (name, random.randint(0, 1000000000))
    return UserTuple(name=name, email='%s@chalab.test' % name, password='sadhasdjasdqwdnasdbkj')


def register(c, u):
    r = c.post(reverse('account_signup'),
               {'username': u.name, 'email': u.email,
                'password1': u.password, 'password2': u.password})
    return r


def q2(f, c=None):
    c = c or Client()
    r = c.get(reverse(f))
    html = BeautifulSoup(r.content, 'html.parser')
    return r, html


def q(f, c=None):
    _, html = q2(f, c=c)
    return html
