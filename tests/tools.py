import os
import random
from collections import namedtuple

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.core import mail
from django.http import QueryDict
from django.template.response import ContentNotRenderedError
from django.test import Client
from django.test import RequestFactory
from django.urls import reverse
from django.utils.six.moves.urllib.parse import (urljoin, urlsplit)

UserTuple = namedtuple('UserTuple', ['name', 'email', 'password'])
ClientQueryTuple = namedtuple('ClientQueryTuple', ['client', 'response', 'html'])

_FACTORY = RequestFactory()


# Asserting Tools
# ===============

def assert_redirects(response, expected_url, status_code=302, target_status_code=200):
    """
    Naive reimplementation of Django's assertRedirects.
    Compatible with pytest and should preserve its better error reporting.

    https://docs.djangoproject.com/en/1.10/_modules/django/test/testcases/#SimpleTestCase.assertRedirects
    """
    assert response.status_code == status_code, \
        "got status=%s instead of %s" % (response.status_code, status_code)

    url = response.url
    scheme, netloc, path, query, fragment = urlsplit(url)

    url = urljoin(response.request['PATH_INFO'], url)
    path = urljoin(response.request['PATH_INFO'], path)

    redirect_response = response.client.get(path, QueryDict(query), secure=(scheme == 'https'))
    assert redirect_response.status_code == target_status_code, \
        "got status=%s instead of %s" % (redirect_response.status_code, target_status_code)
    assert url == expected_url, \
        "got url=%s instead of %s" % (url, expected_url)


# File & Dirs manipulation
# ========================

def file_dir(__file__, *suffix):
    """
    Return the directory for the passed `__file__' constant.
    Append an optional suffix to it.

    Used to load resources relative to the current file for example.
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), *suffix)


def test_dir(*suffix):
    """
    Return the directory relative to the root of the test directory.
    """
    return file_dir(__file__, *suffix)


# Mail & Django related
# =====================

def last_mail():
    return mail.outbox[-1]


# Making users and requests
# =========================

def random_user_desc(name):
    name = '%s.%010d' % (name, random.randint(0, 1000000000))
    return UserTuple(name=name, email='%s@chalab.test' % name, password='sadhasdjasdqwdnasdbkj')


def make_user(desc):
    return User.objects.create(username=desc.name, email=desc.email, password=desc.password)


def make_request(url, user=None):
    r = _FACTORY.get(url)

    if user is not None:
        r.user = user

    return r


def html(response):
    try:
        c = response.content
    except ContentNotRenderedError:
        response.render()
        c = response.content

    return BeautifulSoup(c, 'html.parser')


def register(client, user_desc):
    r = client.post(reverse('account_signup'),
                    {'username': user_desc.name, 'email': user_desc.email,
                     'password1': user_desc.password, 'password2': user_desc.password})
    return r


def query(f, c=None):
    """
    Query the view function F, using the given client C (or create one).
    Return a ClientQueryTuple(client, response, html)
    """
    c = c or Client()
    r = c.get(reverse(f))
    h = html(r)
    return ClientQueryTuple(client=c, response=r, html=h)
