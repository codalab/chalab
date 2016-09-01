import pytest
from django.test import Client
from django.urls import reverse

from tests.tools import query
from wizard.models import DocumentationPageModel, DocumentationModel

pytestmark = pytest.mark.django_db

PAGES = ['base', 'evaluation', 'data', 'rules']


def test_documentation_returns_200(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.get(reverse('wizard:challenge:documentation', kwargs={'pk': pk}))

    assert r.status_code == 200


def test_documentation_pass_the_4_pages_by_default(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    r = c.get(reverse('wizard:challenge:documentation', kwargs={'pk': pk}))

    assert len(r.context['pages']) == len(PAGES)
    assert [x.title for x in r.context['pages']] == PAGES


def test_documentation_shows_the_4_pages_by_default(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    q = query('wizard:challenge:documentation', c=c, kwargs={'pk': pk})
    h = q.html

    assert h.select_one('.title').text == 'Documentation'
    assert len(h.select('.page')) == len(PAGES)
    assert [x.text for x in h.select('.page .title')] == PAGES


def test_documentation_page_links_to_the_edition_page(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    q = query('wizard:challenge:documentation', c=c, kwargs={'pk': pk})
    h = q.html

    s = h.select('.page')[0]
    title = s.select_one('.title').text
    a = s.select_one('a.edit')

    pid = DocumentationPageModel.objects.get(title=title).id

    assert a is not None
    assert a['href'] == reverse('wizard:challenge:documentation.page',
                                kwargs={'pk': pk, 'page_id': pid})


def test_edit_page_returns_200(random_challenge):
    pk = random_challenge.challenge.pk
    d = random_challenge.desc
    c = Client()
    assert c.login(username=d.username, password=d.password)

    # TODO(laurent): Instead of querying the view (time dependency)
    #                to create the documentation model
    #                provide a create method in the challenge object.
    q = query('wizard:challenge:documentation', c=c, kwargs={'pk': pk})

    d = DocumentationModel.objects.get(challenge=random_challenge.challenge)
    p = d.pages.first()

    r = c.get(reverse('wizard:challenge:documentation.page',
                      kwargs={'pk': pk, 'page_id': d.id}))

    assert r.status_code == 200
