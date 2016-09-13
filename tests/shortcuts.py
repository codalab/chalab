import pytest
from django.test import Client
from django.urls import reverse

from .tools import html

from lxml import html as lhtml

class SResponse(object):
    def __init__(self, django_response):
        self._response = django_response

    @property
    def status_code(self):
        return self._response.status_code

    @property
    def context(self):
        return self._response.context

    @property
    def content(self):
        return self._response.content

    @property
    def html(self):
        return html(self._response)

    @property
    def lhtml(self):
        return lhtml.fromstring(self._response.content)

    @property
    def url(self):
        return self._response.url

    @property
    def client(self):
        return self._response.client


class SClient(object):
    def __init__(self, django_client):
        self._client = django_client

    def post(self, view, data=None, **kwargs):
        return SResponse(self._client.post(reverse(view, kwargs=kwargs), data=data))

    def get(self, view, **kwargs):
        return SResponse(self._client.get(reverse(view, kwargs=kwargs)))

    @classmethod
    def logged(cls, desc):
        client = Client()
        assert client.login(username=desc.username, password=desc.password)
        return cls(client)


@pytest.fixture(scope='function')
def c(challenge_ready):
    """
    A shortcut client to test challenge.

    Returns a Client with
    client.challenge, the challenge object
    client.pk, the challenge pk
    """
    client = SClient.logged(challenge_ready.desc)

    client.challenge = challenge_ready.challenge
    client.pk = challenge_ready.challenge.pk
    return client


@pytest.fixture(scope='function')
def cb(random_challenge):
    """
    A shortcut client to test challenge.

    Returns a Client with
    client.challenge, the challenge object
    client.pk, the challenge pk
    """
    client = SClient.logged(random_challenge.desc)

    client.challenge = random_challenge.challenge
    client.pk = random_challenge.challenge.pk
    return client
