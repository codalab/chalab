from django.test import Client
from django.test import TestCase
from django.urls import reverse

from wizard import models, views
from ..tools import register, q, q2, random_user, make_request, html

NAV_LOGGED = ['home', 'about', 'login']


class HomePageTest(TestCase):
    def test_home_after_login_returns_200(self):
        c = Client()
        register(c, random_user('richard_f'))

        r = c.get(reverse('wizard:home'))

        self.assertEqual(r.status_code, 200)

    def test_home_after_login_is_app_wizard(self):
        c = Client()
        register(c, random_user('nikola_t'))

        home = q('wizard:home', c)
        app = home.select('.app')

        self.assertEqual(len(app), 1)
        self.assertEqual(app[0]['id'], 'wizard')

    def test_home_after_login_shows_empty_list_of_challenges(self):
        c = Client()
        register(c, random_user('richard_f'))

        home = q('wizard:home', c)

        challenges_block = home.select('.challenges')
        challenges = home.select('.challenges .challenge')
        self.assertEqual(len(challenges_block), 1)
        self.assertEqual(len(challenges), 0)

    def test_home_shows_create_challenge_button(self):
        c = Client()
        register(c, random_user('richard_f'))

        home = q('wizard:home', c)

        create_btn = home.select('a.create-challenge')[0]
        self.assertEqual(create_btn['href'], reverse('wizard:create'))

    def test_home_without_login_returns_403(self):
        r = Client().get(reverse('wizard:home'))

        self.assertRedirects(r, '/accounts/login/?next=/wizard/')

        # def test_home_shows_create_competition(self):
        #     c, _ = register('nikola_t')
        #     r = c.get(reverse('wizard:home'))

    def test_shows_challenges(self):
        c = Client()
        r = register(c, random_user('richard_f'))
        u = r.context['user']

        models.ChallengeModel.objects.create(title='a challenge',
                                             organization_name='the organization',
                                             description='the description',
                                             created_by=u)

        r = c.get(reverse('wizard:home'))

        self.assertEqual(len(r.context['object_list']), 1)

    def test_shows_challenges_bis(self):
        c = Client()
        r = register(c, random_user('richard_f'))
        u = r.context['user']

        models.ChallengeModel.objects.create(title='a challenge',
                                             organization_name='the organization',
                                             description='the description',
                                             created_by=u)

        html = q('wizard:home', c)
        challenges = html.select('.challenges .challenge')

        self.assertEqual(len(challenges), 1)


def random_text(name, length):
    return '%s_%s' % (name, 'x' * (length - len(name) - 1))


def make_challenge(user, title=None, description=None, organization_name=None):
    title = title or random_text('title', 30)
    description = description or random_text('description', 120)
    organization_name = organization_name or random_text('organization_name', 30)

    return models.ChallengeModel.objects.create(created_by=user, title=title,
                                                description=description,
                                                organization_name=organization_name)


class WizardDataDefinition(TestCase):
    def test_url_exists(self):
        r = reverse('wizard:data', kwargs=dict(pk=1))
        assert r is not None


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

    def test_challenge_page_shows_links_to_data(self):
        request = make_request('/', user=random_user('john_doe'))
        c = make_challenge(user=request.user)

        r = views.ChallengeDescriptionDetail.as_view()(request, pk=c.pk)
        r = html(r)

        self.assertEqual(r.select('.flow .data a')[0]['href'],
                         reverse('wizard:data', kwargs=dict(pk=c.pk)))
