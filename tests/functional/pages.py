import logging
import random
from collections import namedtuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException

log = logging.getLogger('pages')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

UserTuple = namedtuple('UserTuple', ['name', 'email', 'password'])


def random_user(name):
    name = '%s.%010d' % (name, random.randint(0, 1000000000))
    return UserTuple(name=name, email='%s@chalab.test' % name, password='sadhasdjasdqwdnasdbkj')


class SelectableMixin(object):
    @property
    def selectable(self):
        try:
            return self.elem
        except AttributeError:
            return self.driver

    def by_css(self, selector, on_missing=Exception):
        try:
            return self.selectable.find_element_by_css_selector(selector)
        except (NoSuchElementException, TimeoutException) as e:
            if on_missing != Exception:
                return on_missing
            else:
                raise e

    def by_css_many(self, selector, on_missing=Exception, clss=None):
        try:
            xs = self.selectable.find_elements_by_css_selector(selector)
        except (NoSuchElementException, TimeoutException) as e:
            if on_missing != Exception:
                return on_missing
            else:
                raise e

        if clss is not None:
            return [clss(self, x) for x in xs]
        else:
            return xs


class FormBlock(SelectableMixin):
    def __init__(self, parent, elem):
        self.driver = parent.driver
        self.elem = elem

    def has_fields(self, inputs=[]):
        for i in inputs:
            if not self.by_css('input#id_%s' % i, on_missing=False):
                return False

        return True

    def fill(self, **kwargs):
        for (k, v) in kwargs.items():
            try:
                self.by_css('input#id_%s' % k).send_keys(v)
            except (NoSuchElementException, TimeoutException):
                self.by_css('textarea#id_%s' % k).send_keys(v)

        return self

    def submit(self):
        self.elem.submit()
        return self


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


class Page(SelectableMixin):
    def __init__(self, driver):
        self.driver = driver

    def get(self, url):
        self.driver.get(url)
        return self

    def nav_to(self, page_name):
        self.by_css('nav #%s a' % page_name).click()
        return self

    def click_on_logo(self):
        self.by_css('header #logo a').click()
        return self

    def click(self, selector):
        self.by_css(selector).click()
        return self

    def form(self, selector):
        return FormBlock(self, self.by_css('form%s' % selector))

    def is_app(self, name, panel=None):
        a = self.by_css('.app#%s' % name, on_missing=None) is not None

        if not a:
            log.error('not app=%s', name)

        if panel is not None:
            p = self.by_css('.panel#%s' % panel, on_missing=None) is not None

            if not p:
                log.error('not panel=%s', panel)

            a = a and p

        return a

    def capture(self, name):
        self.driver.save_screenshot(name + '.png')

    @property
    def challenges(self):
        return ChallengesBlock(self)
