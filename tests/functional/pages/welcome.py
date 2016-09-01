from .core import Page, FormBlock
from .wizard import WizardPage


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

    def register(self, username, email, password):
        f = self.form
        f.fill(username=username, email=email,
               password1=password, password2=password).submit()
        return WizardPage(self)
