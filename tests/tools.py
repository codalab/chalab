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

UserTuple = namedtuple('UserTuple', ['username', 'email', 'password'])
ChallengeTuple = namedtuple('ChallengeTuple', ['title', 'org_name', 'description'])
ClientQueryTuple = namedtuple('ClientQueryTuple', ['client', 'response', 'html'])

_FACTORY = RequestFactory()


# Asserting Tools
# ===============

def assert_redirects(response, expected_url,
                     status_code=302, target_status_code=200,
                     fetch_redirect_response=True):
    """
    Naive reimplementation of Django's assertRedirects.
    Compatible with pytest and should preserve its better error reporting.

    https://docs.djangoproject.com/en/1.10/_modules/django/test/testcases/#SimpleTestCase.assertRedirects
    """
    assert response.status_code == status_code, \
        "got status=%s instead of %s" % (response.status_code, status_code)

    url = response.url
    scheme, netloc, path, query, fragment = urlsplit(url)

    # Prepend path for relative redirects.
    if not path.startswith('/'):
        url = urljoin(response.request['PATH_INFO'], url)
        path = urljoin(response.request['PATH_INFO'], path)

    assert url == expected_url, \
        "got url=%s instead of %s" % (url, expected_url)

    if fetch_redirect_response:
        redirect_response = response.client.get(path, QueryDict(query), secure=(scheme == 'https'))
        assert redirect_response.status_code == target_status_code, \
            "got status=%s instead of %s" % (redirect_response.status_code, target_status_code)


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

def random_user_desc(username):
    username = '%s.%010d' % (username, random.randint(0, 1000000000))
    return UserTuple(username=username,
                     email='%s@chalab.test' % username,
                     password='sadhasdjasdqwdnasdbkj')


def random_challenge_desc(name):
    title = '%s.%010d' % (name, random.randint(0, 1000000000))
    org_name = '%s.org.%010d' % (name, random.randint(0, 1000000000))
    desc = '%s.desc.%010d' % (name, random.randint(0, 1000000000))
    return ChallengeTuple(title=title,
                          org_name=org_name,
                          description=desc)


def make_user(desc):
    return User.objects.create_user(username=desc.username, email=desc.email,
                                    password=desc.password)


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
                    {'username': user_desc.username, 'email': user_desc.email,
                     'password1': user_desc.password, 'password2': user_desc.password})
    return r


def query(f, c=None, kwargs={}):
    """
    Query the view function F, using the given client C (or create one).
    Return a ClientQueryTuple(client, response, html)
    """
    c = c or Client()
    r = c.get(reverse(f, kwargs=kwargs))
    h = html(r)
    return ClientQueryTuple(client=c, response=r, html=h)


# Simplif Tools
# =============

def sreverse(viewname, **kwargs):
    return reverse(viewname, kwargs=kwargs)
