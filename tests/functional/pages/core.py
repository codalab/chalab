import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException

log = logging.getLogger('functional.pages')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


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

    def click(self, selector):
        self.by_css(selector).click()


class CapturableMixin(object):
    def capture(self, name):
        self.driver.save_screenshot(name + '.png')


class BasicElementsMixin(object):
    @property
    def h1(self):
        return self.by_css('h1')


class Block(SelectableMixin, CapturableMixin, BasicElementsMixin):
    selector = None

    def __init__(self, parent):
        assert self.selector is not None, "define a selector for this block."
        self.parent = parent
        self.driver = parent.driver
        self.elem = self.by_css(self.selector)


class FormBlock(Block):
    def has_fields(self, inputs):
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


class HeroBlock(Block):
    selector = '.hero'
    selector_lead = '.lead'

    @property
    def lead(self):
        return self.by_css(self.selector_lead)


class Page(SelectableMixin, CapturableMixin, BasicElementsMixin):
    selector_content = '.content'

    def __init__(self, driver_or_prev):
        try:
            self.driver = driver_or_prev.driver
            self.prev = driver_or_prev
        except AttributeError:
            self.driver = driver_or_prev
            self.prev = None

    def get(self, url):
        self.driver.get(url)
        return self

    @property
    def content(self):
        return self.by_css(self.selector_content)

    @property
    def hero(self):
        return HeroBlock(self)

    def nav_to(self, page_name):
        self.by_css('nav #%s a' % page_name).click()
        return self

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
