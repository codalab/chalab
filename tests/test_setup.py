import pytest

from chalab import chacelery
from wizard import tasks as wizard


@pytest.mark.timeout(5)
def test_celery_setup():
    a = chacelery.smoke.delay(42)
    r = a.get()
    assert r == 42


@pytest.mark.timeout(5)
def test_celery_tasks_setup():
    a = wizard.smoke.delay(51)
    r = a.get()
    assert r == 51
