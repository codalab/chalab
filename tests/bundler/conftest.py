import pytest

from tests.wizard.conftest import random_challenge
from wizard import models

random_challenge = random_challenge


@pytest.fixture(scope='function')
def challenge_ready(random_challenge):
    c = random_challenge.challenge
    c.documentation = models.DocumentationModel.create(render_for=c)

    # TODO: fill challenge to be ready for export
    return random_challenge
