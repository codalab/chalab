import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.tools import file_dir
from tests.wizard.conftest import random_challenge, challenge_ready
from tests.wizard.tools import CHALEARN_SAMPLE
from wizard import models

random_challenge = random_challenge
challenge_ready = challenge_ready



