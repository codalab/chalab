from collections import namedtuple

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from tests.tools import make_request, random_user_desc, html, register, make_user, file_dir
from tests.wizard.models.tools import make_challenge
from tests.wizard.tools import CHALEARN_SAMPLE
from wizard import models
from wizard import views as wizard_views

ChallengeTuple = namedtuple('ChallengeTuple', ['user', 'desc', 'challenge', 'response', 'html'])
UserTuple = namedtuple('UserTuple', ['client', 'desc', 'registration', 'user'])

LOGO_PATH = file_dir(__file__, 'resources', 'logo.png')


@pytest.fixture(scope='function')
def random_user():
    c = Client()
    desc = random_user_desc('richard_f')
    r = register(c, desc)

    return UserTuple(client=c, desc=desc, registration=r, user=r.context['user'])


@pytest.fixture(scope='function')
def random_challenge():
    """Return the challenge and corresponding view"""
    desc = random_user_desc('john_doe')
    user = make_user(desc)
    request = make_request('/', user=user)

    chall = make_challenge(user=request.user)
    resp = wizard_views.ChallengeDescriptionDetail.as_view()(request, pk=chall.pk)
    h = html(resp)

    return ChallengeTuple(user=request.user, desc=desc, challenge=chall, response=resp, html=h)


@pytest.fixture(scope='function')
def challenge_ready(random_challenge):
    # TODO(laurent): This code should be in the model part, like random_challenge
    c = random_challenge.challenge
    c.documentation = models.DocumentationModel.create(render_for=c)
    c.dataset = models.DatasetModel.from_chalearn(CHALEARN_SAMPLE, 'chalearn - sample')
    c.task = models.TaskModel.from_chalearn(c.dataset, CHALEARN_SAMPLE, 'chalearn - task sample')

    c.logo = SimpleUploadedFile(name='my_logo.png',
                                content=open(LOGO_PATH, 'rb').read(),
                                content_type='image/png')

    c.metric = models.MetricModel.objects.create(owner=None, is_public=True,
                                                 name='some metric', is_ready=True,
                                                 classification=True)
    c.protocol = models.ProtocolModel.objects.create(is_ready=True)

    c.save()

    assert c.missings == []
    assert c.is_ready

    # TODO: fill challenge to be ready for export
    return random_challenge


from tests.shortcuts import cb

cb = cb
