from django.test import Client
from django.test import TestCase
from django.urls import reverse

from tests.tools import register, q, random_user
from wizard import models

NAV_LOGGED = ['home', 'about', 'login']


class HomePageTest(TestCase):
    def test_after_login_returns_200(self):
        c = Client()
        register(c, random_user('richard_f'))

        r = c.get(reverse('wizard:home'))

        self.assertEqual(r.status_code, 200)

    def test_without_login_returns_403(self):
        r = Client().get(reverse('wizard:home'))

        self.assertRedirects(r, '/accounts/login/?next=/wizard/')

    def test_after_login_is_app_wizard(self):
        c = Client()
        register(c, random_user('nikola_t'))

        home = q('wizard:home', c)
        app = home.select('.app')

        self.assertEqual(len(app), 1)
        self.assertEqual(app[0]['id'], 'wizard')

    def test_after_login_shows_empty_list_of_challenges(self):
        c = Client()
        register(c, random_user('richard_f'))

        home = q('wizard:home', c)

        challenges_block = home.select('.challenges')
        challenges = home.select('.challenges .challenge')
        self.assertEqual(len(challenges_block), 1)
        self.assertEqual(len(challenges), 0)

    def test_shows_create_challenge_button(self):
        c = Client()
        register(c, random_user('richard_f'))

        home = q('wizard:home', c)

        create_btn = home.select('a.create-challenge')[0]
        self.assertEqual(create_btn['href'], reverse('wizard:create'))

    def test_challenge_is_in_context(self):
        c = Client()
        r = register(c, random_user('richard_f'))
        u = r.context['user']

        m = models.ChallengeModel.objects.create(title='a challenge',
                                                 organization_name='the organization',
                                                 description='the description',
                                                 created_by=u)

        r = c.get(reverse('wizard:home'))

        self.assertEqual(r.context['object_list'].count(), 1)
        self.assertEqual(r.context['object_list'].first(), m)

    def test_challenge_is_in_html(self):
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
