from selenium.webdriver.support.select import Select

from .core import Page, SelectableMixin, FormBlock, Block


class LoggedPage(Page):
    @property
    def user(self):
        try:
            return self._user
        except AttributeError:
            return self.prev.user

    @property
    def challenge(self):
        try:
            return self._challenge
        except AttributeError:
            return self.prev.challenge

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


class GroupOfBlocks(SelectableMixin):
    selector = None
    block_clss = None

    def __init__(self, parent):
        self.driver = parent.driver
        self.elem = parent.by_css(self.selector)

    @property
    def all(self):
        return self.by_css_many(self.block_clss.selector,
                                clss=self.block_clss, on_missing=[])

    def __getitem__(self, item):
        return self.all[item]

    def __len__(self):
        return len(self.all)

    def get(self, clss=None):
        r = self.all

        if clss is not None:
            r = [x for x in r if clss in x.elem.get_attribute('class')]

        assert len(r) == 1
        return r[0]


class ChallengesBlock(GroupOfBlocks):
    selector = '.challenges'
    block_clss = ChallengeBlock


class PanelBlock(Block):
    selector_body = '.panel-body'
    selector_heading = '.panel-heading'

    @property
    def body(self):
        return self.by_css(self.selector_body)

    @property
    def heading(self):
        return self.by_css(self.selector_heading)


class DescriptionBlock(PanelBlock):
    selector = '.description'


class StepBlock(SelectableMixin):
    selector = '.step'
    selector_link = '.title a'
    selector_ready = '.ready'

    def __init__(self, parent, elem):
        self.driver = parent.driver
        self.elem = elem

    def click(self, selector=None):
        assert selector is None
        self.by_css(self.selector_link).click()

    @property
    def is_ready(self):
        return self.by_css(self.selector_ready, on_missing=None) is not None


class StepBlocks(GroupOfBlocks):
    selector = '.flow-full'
    block_clss = StepBlock


class DefinitionBlock(PanelBlock):
    selector = '.definition'

    @property
    def steps(self):
        return StepBlocks(self)


class PublicPickerDataForm(FormBlock):
    selector = '.pick .public form'

    def pick(self, name):
        s = Select(self.by_css('select[name="dataset"]'))
        s.select_by_visible_text(name)


class PublicPickerMetricForm(FormBlock):
    selector = '.pick .public form'

    def pick(self, name):
        s = Select(self.by_css('select[name="metric"]'))
        s.select_by_visible_text(name)


class FlowBlock(Block):
    selector = '.flow'

    selector_next = '.next a'
    selector_up = '.up a'

    @property
    def next(self):
        return self.by_css(self.selector_next)

    @property
    def up(self):
        return self.by_css(self.selector_up)


class ChallengeFlowPage(LoggedPage):
    app = 'wizard'

    @property
    def flow(self):
        return FlowBlock(self)

    def next(self):
        self.flow.next.click()
        return ChallengeTaskPage(self).checked()

    def up(self):
        self.flow.up.click()
        return DetailChallengePage(self).checked()


class ChallengeMetricPage(ChallengeFlowPage):
    panel = 'challenge-metric'

    picker_module = 'picker'
    editor_module = 'editor'

    @property
    def is_picker(self):
        return self.is_module(self.picker_module)

    @property
    def is_editor(self):
        return self.is_module(self.editor_module)

    @property
    def picker_form_public(self):
        return PublicPickerMetricForm(self)

    def pick_metric(self, public, name):
        if public:
            f = self.picker_form_public
        else:
            f = None

        f.pick(name)
        f.submit()
        return self


class ChallengeTaskPage(ChallengeFlowPage):
    panel = 'challenge-task'


class ProtocolForm(FormBlock):
    selector = '.protocol form'


class ChallengeProtocolPage(ChallengeFlowPage):
    panel = 'challenge-protocol'

    @property
    def form(self):
        return ProtocolForm(self)

    def set(self, values):
        self.form.fill(**values)
        self.form.submit()
        return self


class ChallengeDataPage(ChallengeFlowPage):
    panel = 'challenge-data'

    picker_module = 'picker'
    editor_module = 'editor'

    @property
    def is_picker(self):
        return self.is_module(self.picker_module)

    @property
    def is_editor(self):
        return self.is_module(self.editor_module)

    @property
    def picker_form_public(self):
        return PublicPickerDataForm(self)

    def pick_dataset(self, public, name):
        if public:
            f = self.picker_form_public
        else:
            f = None

        f.pick(name)
        f.submit()
        return self


class DetailChallengePage(LoggedPage):
    app = 'wizard'
    panel = 'challenge'

    def __init__(self, driver_or_prev, challenge=None):
        self._challenge = challenge or driver_or_prev.challenge
        super().__init__(driver_or_prev)

    @property
    def description(self):
        return DescriptionBlock(self)

    @property
    def definition(self):
        return DefinitionBlock(self)

    def click_step(self, name):
        self.definition.steps.get(clss=name).click()

    def to_data(self):
        self.click_step('data')
        return ChallengeDataPage(self).checked()

    def to_metric(self):
        self.click_step('metric')
        return ChallengeMetricPage(self).checked()

    def to_protocol(self):
        self.click_step('protocol')
        return ChallengeProtocolPage(self).checked()


class ChallengeForm(FormBlock):
    selector = '.challenge'


class CreateChallengePage(LoggedPage):
    @property
    def form(self):
        return ChallengeForm(self)

    def submit(self, c):
        f = self.form

        f.fill(title=c.title, organization_name=c.org_name, description=c.description).submit()
        return DetailChallengePage(self, challenge=c)


class WizardPage(LoggedPage):
    selector_create_challenge = '.create-challenge'

    def __init__(self, driver_or_prev, user=None):
        super().__init__(driver_or_prev)

        if user is not None:
            self._user = user

    @property
    def challenges(self):
        return ChallengesBlock(self)

    def create_challenge(self):
        self.click(self.selector_create_challenge)
        return CreateChallengePage(self)
