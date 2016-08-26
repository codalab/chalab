import random
import string

from tests.tools import test_dir
from wizard import models


def random_text(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def random_name(prefix, length):
    return '%s_%s' % (prefix, random_text(length - len(prefix) - 1))


def make_challenge(user, title=None, description=None, organization_name=None):
    title = title or random_name('title', 30)
    description = description or random_name('description', 120)
    organization_name = organization_name or random_name('organization_name', 30)

    return models.ChallengeModel.objects.create(created_by=user, title=title,
                                                description=description,
                                                organization_name=organization_name)


# Resources definitions

COLUMNS_5 = test_dir('wizard', 'resources', 'columns_5.csv')
COLUMNS_12 = test_dir('wizard', 'resources', 'columns_12.csv')
MATRIX_5_3 = test_dir('wizard', 'resources', 'matrix_5x3.csv')
CHALEARN_SAMPLE = test_dir('wizard', 'resources', 'adult')
CHALEARN_SAMPLE_SPARSE = test_dir('wizard', 'resources', 'sparse')
CHALEARN_SAMPLE_WRONG_ROWS = test_dir('wizard', 'resources', 'adult_wrong_rows')
CHALEARN_SAMPLE_WRONG_FEAT_SPEC = test_dir('wizard', 'resources', 'adult_wrong_feat_spec')
CHALEARN_SAMPLE_WITHOUT_FEAT_SPEC = test_dir('wizard', 'resources', 'adult_without_feat_spec')
