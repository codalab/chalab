import random
import string

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
