import os
from collections import namedtuple

from tests.wizard import tools
from tests.wizard.tools import random_name
from wizard import models

FakeNamedObject = namedtuple('FakeNamedObject', ['name'])


def create_with_file(clss, file_path, **kwargs):
    """
    Helper class to test ColumXXXX and MatrixXXX classes,
    the one that stores files in their x.raw_content field.

    Handles the file storage.
    """
    c = clss(**kwargs)
    base_name = os.path.basename(file_path)
    with open(file_path, 'r') as f:
        c.raw_content.save(base_name, f)
    c.save()
    return c


def make_samples_datasets():
    d1 = models.DatasetModel.from_chalearn(tools.CHALEARN_SAMPLE, 'chalearn - sample')
    d2 = models.DatasetModel.from_chalearn(tools.CHALEARN_SAMPLE_SPARSE, 'chalearn.sparse - sample')

    return d1, d2


def make_challenge(user, title=None, description=None, organization_name=None):
    title = title or random_name('title', 30)
    description = description or random_name('description', 120)
    organization_name = organization_name or random_name('organization_name', 30)

    return models.ChallengeModel.objects.create(created_by=user, title=title,
                                                description=description,
                                                organization_name=organization_name)
