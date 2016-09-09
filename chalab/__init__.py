import os

HERE = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(HERE, 'VERSION'), 'r') as f:
    __version__ = f.readline().strip()

from .chacelery import app as celery_app

celery_app = celery_app  # avoid unused warnings
