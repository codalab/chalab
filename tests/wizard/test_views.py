from django.test import Client
from django.test import TestCase
from django.urls import reverse

from wizard import models
from ..tools import register, q, q2

NAV_LOGGED = ['home', 'about', 'login']


class HomePageTest(TestCase):
    def test_home_after_login_returns_200(self):
        c, _ = register('richard_f')
        r = c.get(reverse('wizard:home'))
        self.assertEqual(r.status_code, 200)

    def test_home_after_login_is_app_wizard(self):
        c, _ = register('nikola_t')

        home = q('wizard:home', c)
        app = home.select('.app')

        self.assertEqual(len(app), 1)
        self.assertEqual(app[0]['id'], 'wizard')

    def test_home_after_login_shows_empty_list_of_challenges(self):
        c, _ = register('gauss_c')

        home = q('wizard:home', c)

        challenges_block = home.select('.challenges')
        challenges = home.select('.challenges .challenge')
        self.assertEqual(len(challenges_block), 1)
        self.assertEqual(len(challenges), 0)

    def test_home_shows_create_challenge_button(self):
        c, _ = register('nietzsche_f')

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
        c, r = register('edison_t')
        u = r.context['user']

        models.ChallengeModel.objects.create(title='a challenge',
                                             organization_name='the organization',
                                             description='the description',
                                             created_by=u)

        r = c.get(reverse('wizard:home'))

        self.assertEqual(len(r.context['object_list']), 1)

    def test_shows_challenges_bis(self):
        c, r = register('edison_t')
        u = r.context['user']

        models.ChallengeModel.objects.create(title='a challenge',
                                             organization_name='the organization',
                                             description='the description',
                                             created_by=u)

        html = q('wizard:home', c)
        challenges = html.select('.challenges .challenge')

        self.assertEqual(len(challenges), 1)


class WizardFlowCreation(TestCase):
    def test_create_challenge_shows_challenge_form(self):
        c, _ = register('curie_m')
        r, html = q2('wizard:create', c)
        self.assertTrue('form' in r.context)

    def test_create_challenges_shows_panel_1create(self):
        c, _ = register('curie_p')
        r, html = q2('wizard:create', c)
        self.assertEqual(html.select('.panel')[0]['id'], 'create-challenge')

    def test_create_challenges_redirect_to_challenge(self):
        c, r = register('darwin_c')
        u = r.context['user']

        r = c.post(reverse('wizard:create'),
                   {'title': 'A challenge',
                    'organization_name': 'an organization',
                    'description': 'the description'})

        last_challenge = models.ChallengeModel.objects.filter(created_by=u).last()

        self.assertRedirects(r, reverse('wizard:challenge', kwargs={'pk': last_challenge.pk}))
