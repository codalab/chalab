from .core import Page, FormBlock
from .wizard import WizardPage
from tests.tools import UserTuple, ChallengeTuple


class SignupForm(FormBlock):
    selector = '.signup'


class HomePage(Page):
    def about(self):
        self.nav_to('about')
        return AboutPage(self)

    def signup(self):
        self.nav_to('signup')
        return SignupPage(self)

    def click_logo(self):
        self.by_css('header #logo a').click()
        return HomePage(self)


class AboutPage(HomePage):
    pass


class SignupPage(HomePage):
    @property
    def form(self):
        return SignupForm(self)

    def register(self, user_tuple):
        f = self.form
        f.fill(username=user_tuple.username, email=user_tuple.email,
               password1=user_tuple.password, password2=user_tuple.password).submit()
        return WizardPage(self, user=user_tuple)
