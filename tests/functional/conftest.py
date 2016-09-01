import pytest

from tests import selen
from .pages import HomePage


@pytest.fixture(scope='function')
def raw_driver():
    d = selen.raw_driver()
    try:
        yield d
    finally:
        d.close()


@pytest.fixture(scope='function')
def home(raw_driver):
    raw_driver.get(selen.LIVE_SERVER_URL)
    return HomePage(raw_driver)
