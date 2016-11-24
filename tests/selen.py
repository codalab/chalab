import os

from seleniumrequests import Chrome, Firefox, PhantomJS, Remote

# TODO(laurent): All the options for this part is under-tested. Recap how a user may override
#                these options.
LIVE_SERVER_URL = os.environ.get('TEST_LIVE_SERVER_URL', 'http://localhost:8000')

SELENIUM_DRIVER = os.environ.get('SELENIUM_DRIVER', 'phantomjs')
SELENIUM_REMOTE_URL = os.environ.get('SELENIUM_REMOTE_URL', 'http://127.0.0.1:4444/wd/hub')
SELENIUM_REMOTE_DRIVER = os.environ.get('SELENIUM_REMOTE_DRIVER', 'firefox')

_HERE = os.path.dirname(os.path.realpath(__file__))

_DRIVERS = {
    'chrome': lambda: Chrome(executable_path=os.path.join(_HERE, 'chromedriver')),
    'firefox': Firefox,
    'phantomjs': PhantomJS,
    'remote': lambda: Remote(command_executor=SELENIUM_REMOTE_URL,
                             desired_capabilities={'browserName': SELENIUM_REMOTE_DRIVER})
}

CURRENT_DRIVER = _DRIVERS['phantomjs']


def raw_driver():
    driver = CURRENT_DRIVER()
    driver.default_wait = 5
    driver.get(LIVE_SERVER_URL)
    return driver
