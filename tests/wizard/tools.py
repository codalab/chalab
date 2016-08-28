import random
import string

from tests.tools import test_dir


def random_text(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def random_name(prefix, length):
    return '%s_%s' % (prefix, random_text(length - len(prefix) - 1))


# Resources definitions

COLUMNS_5 = test_dir('wizard', 'resources', 'columns_5.csv')
COLUMNS_12 = test_dir('wizard', 'resources', 'columns_12.csv')
MATRIX_5_3 = test_dir('wizard', 'resources', 'matrix_5x3.csv')
CHALEARN_SAMPLE = test_dir('wizard', 'resources', 'adult')
CHALEARN_SAMPLE_SPARSE = test_dir('wizard', 'resources', 'sparse')
CHALEARN_SAMPLE_WRONG_ROWS = test_dir('wizard', 'resources', 'adult_wrong_rows')
CHALEARN_SAMPLE_WRONG_FEAT_SPEC = test_dir('wizard', 'resources', 'adult_wrong_feat_spec')
CHALEARN_SAMPLE_WITHOUT_FEAT_SPEC = test_dir('wizard', 'resources', 'adult_without_feat_spec')
