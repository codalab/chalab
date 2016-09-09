import pytest

from bundler.models import BundleTaskModel

pytestmark = pytest.mark.django_db


def test_can_create_logs(random_challenge):
    challenge = random_challenge.challenge
    bt = BundleTaskModel.objects.create(challenge=challenge, state=BundleTaskModel.SCHEDULED)

    bt.do_log("This is a description")
    bt.do_log("This is another description")
