from .core import Page, SelectableMixin, FormBlock


class LoggedPage(Page):
    def go_home(self, url):
        self.driver.get(url)
        return WizardPage(self)


class ChallengeBlock(SelectableMixin):
    selector = '.challenge'
    selector_title = '.title'

    def __init__(self, parent, elem):
        self.driver = parent.driver
        self.elem = elem

    @property
    def title(self):
        return self.by_css(self.selector_title).text


class ChallengesBlock(SelectableMixin):
    selector = '.challenges'

    def __init__(self, parent):
        self.driver = parent.driver
        self.elem = parent.by_css(self.selector)

    @property
    def all(self):
        return self.by_css_many(ChallengeBlock.selector, clss=ChallengeBlock, on_missing=[])

    def __getitem__(self, item):
        return self.all[item]

    def __len__(self):
        return len(self.all)


class DetailChallengePage(LoggedPage):
    pass


class ChallengeForm(FormBlock):
    selector = '.challenge'


class CreateChallengePage(LoggedPage):
    @property
    def form(self):
        return ChallengeForm(self)

    def submit(self, title, org_name, description):
        f = self.form
        f.fill(title=title, organization_name=org_name,
               description=description).submit()
        return DetailChallengePage(self)


class WizardPage(LoggedPage):
    selector_create_challenge = '.create-challenge'

    @property
    def challenges(self):
        return ChallengesBlock(self)

    def create_challenge(self):
        self.click(self.selector_create_challenge)
        return CreateChallengePage(self)
