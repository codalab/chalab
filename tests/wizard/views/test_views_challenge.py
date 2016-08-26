from django.test import Client
from django.test import TestCase
from django.urls import reverse

from tests.tools import register, q2, random_user, make_request, html
from tests.wizard.tools import make_challenge
from wizard import models, views


def get_random_challenge_description():
    request = make_request('/', user=random_user('john_doe'))
    c = make_challenge(user=request.user)
    r = views.ChallengeDescriptionDetail.as_view()(request, pk=c.pk)
    r = html(r)

    return c, r


class WizardFlowCreation(TestCase):
    def test_create_challenge_shows_challenge_form(self):
        c = Client()
        r = register(c, random_user('richard_f'))

        r, html = q2('wizard:create', c)
        self.assertTrue('form' in r.context)

    def test_create_challenges_shows_panel_create(self):
        c = Client()
        r = register(c, random_user('richard_f'))

        r, html = q2('wizard:create', c)
        self.assertEqual(html.select('.panel')[0]['id'], 'create-challenge')

    def test_create_challenges_redirect_to_challenge(self):
        c = Client()
        r = register(c, random_user('richard_f'))

        u = r.context['user']

        r = c.post(reverse('wizard:create'),
                   {'title': 'A challenge',
                    'organization_name': 'an organization',
                    'description': 'the description'})

        last_challenge = models.ChallengeModel.objects.filter(created_by=u).last()

        self.assertRedirects(r, reverse('wizard:challenge', kwargs={'pk': last_challenge.pk}))

    def test_challenge_page_shows_link_to_data(self):
        c, r = get_random_challenge_description()

        self.assertEqual(r.select('.flow-full .step.data a')[0]['href'],
                         reverse('wizard:data', kwargs=dict(pk=c.pk)))

    def test_challenge_page_shows_link_to_task(self):
        c, r = get_random_challenge_description()

        self.assertEqual(r.select('.flow-full .step.task a')[0]['href'],
                         reverse('wizard:task', kwargs=dict(pk=c.pk)))

    def test_challenge_page_shows_link_to_metric(self):
        c, r = get_random_challenge_description()

        self.assertEqual(r.select('.flow-full .step.metric a')[0]['href'],
                         reverse('wizard:metric', kwargs=dict(pk=c.pk)))

    def test_challenge_page_shows_link_to_protocol(self):
        c, r = get_random_challenge_description()

        self.assertEqual(r.select('.flow-full .step.protocol a')[0]['href'],
                         reverse('wizard:protocol', kwargs=dict(pk=c.pk)))

    def test_challenge_page_shows_link_to_baseline(self):
        c, r = get_random_challenge_description()

        self.assertEqual(r.select('.flow-full .step.baseline a')[0]['href'],
                         reverse('wizard:baseline', kwargs=dict(pk=c.pk)))

    def test_challenge_page_shows_link_to_documentation(self):
        c, r = get_random_challenge_description()

        self.assertEqual(r.select('.flow-full .step.documentation a')[0]['href'],
                         reverse('wizard:documentation', kwargs=dict(pk=c.pk)))

    def test_challenge_page_shows_link_to_rules(self):
        c, r = get_random_challenge_description()

        self.assertEqual(r.select('.flow-full .step.rules a')[0]['href'],
                         reverse('wizard:rules', kwargs=dict(pk=c.pk)))
