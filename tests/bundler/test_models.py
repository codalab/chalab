import pytest

from bundler.models import BundleTaskModel

pytestmark = pytest.mark.django_db


def test_can_create_logs(random_challenge):
    challenge = random_challenge.challenge
    bt = BundleTaskModel.objects.create(challenge=challenge, state=BundleTaskModel.SCHEDULED)

    bt.add_log("This is a message")
    bt.add_log("This is another message")

    logs = list(bt.logs)
    assert len(logs) == 2
    assert [x.message for x in logs] == ["This is a message",
                                         "This is another message"]
