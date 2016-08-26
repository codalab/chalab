import logging
import os

from django.core.management.base import BaseCommand

from wizard import models

PATH_CHALEARN_DATASET = './datasets/chalearn/'

log = logging.getLogger('wizard.commands.datasets')


def list_folders(dir):
    """
    List all the folders in DIR.
    Returns a list of tuples [(path, folder_name), ...]
    """
    ls = os.listdir(dir)
    ls = [(os.path.join(dir, x), x) for x in ls]
    ls = [x for x in ls if os.path.isdir(x[0])]
    return ls


class Command(BaseCommand):
    help = 'Load the datasets'

    def add_arguments(self, parser):
        pass

    def _warn(self, message):
        self.stderr.write(self.style.WARNING(message))

    def _success(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def handle(self, *args, **options):
        self._warn("You need to run the download script "
                   "first (see the `make dataset') commad")
        self._warn("This command is designed to be run only once "
                   "You need to remove previous datasets by hand.")

        for (path, name) in list_folders(PATH_CHALEARN_DATASET):
            self._success('loading: %s' % path)
            models.DatasetModel.from_chalearn(path, 'Chalearn - ' + name)
            self._success('Successfully loaded: %s' % path)

        self._success('Successfully loaded the datasets')
