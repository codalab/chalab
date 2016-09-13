import pytest

from tests.tools import sreverse
from wizard.models import DocumentationPageModel, DocumentationModel

pytestmark = pytest.mark.django_db

PAGES = sorted(['overview', 'evaluation', 'data', 'terms_and_conditions'])


def test_documentation_returns_200(cb):
    r = cb.get('wizard:challenge:documentation', pk=cb.pk)

    assert r.status_code == 200


def test_documentation_pass_the_4_pages_by_default(cb):
    r = cb.get('wizard:challenge:documentation', pk=cb.pk)

    assert len(r.context['pages']) == len(PAGES)
    assert sorted([x.title for x in r.context['pages']]) == PAGES


def test_documentation_shows_the_4_pages_by_default(cb):
    h = cb.get('wizard:challenge:documentation', pk=cb.pk).html

    assert 'Documentation' in h.select_one('h2').text
    assert len(h.select('.nav-page')) == len(PAGES)
    assert sorted([x.text.strip() for x in h.select('.nav-page')]) == PAGES


def test_documentation_page_links_to_the_specific_page_content(cb):
    h = cb.get('wizard:challenge:documentation', pk=cb.pk).html

    s = h.select('.nav-page')[0]
    title = s.text.strip()
    a = s.select_one('a')

    pid = DocumentationPageModel.objects.get(title=title).id

    assert a is not None
    assert a['href'] == sreverse('wizard:challenge:documentation.page',
                                 pk=cb.pk, page_id=pid)


def test_edit_page_returns_200(cb):
    # TODO(laurent): Instead of querying the view (time dependency)
    #                to create the documentation model
    #                provide a create method in the challenge object.
    cb.get('wizard:challenge:documentation', pk=cb.pk)

    d = DocumentationModel.objects.get(challenge=cb.challenge)
    p = d.pages.first()

    r = cb.get('wizard:challenge:documentation.page',
               pk=cb.pk, page_id=p.id)

    assert r.status_code == 200
