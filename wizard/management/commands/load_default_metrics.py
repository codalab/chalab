import logging

from django.core.management.base import BaseCommand

from wizard import models

log = logging.getLogger('wizard.commands.load_default_metrics')

METRICS = {
    'accuracy_score': {
        'classification': True
    },
    'log_loss': {
        'classification': True
    },
    'roc_auc_score': {
        'classification': True
    },
    'confusion_matrix': {
        'classification': True
    },
    'mean_absolute_error': {
        'regression': True
    },
    'mean_squared_error': {
        'regression': True
    },
    'r2_score': {
        'regression': True
    }
}


class Command(BaseCommand):
    help = 'Load the default metrics'

    def add_arguments(self, parser):
        pass

    def _warn(self, message):
        self.stderr.write(self.style.WARNING(message))

    def _success(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def handle(self, *args, **options):
        self._warn("This command is designed to be run only once "
                   "You need to remove previous metrics by hand.")

        for (name, content) in METRICS.items():
            self._success('loading: %s' % name)
            models.MetricModel.objects.create(
                name=name,
                owner=None,
                is_public=True,
                is_ready=True,
                classification=content.get('classification', False),
                regression=content.get('regression', False),
            )
            self._success('Successfully loaded metric: %s' % name)

        self._success('Successfully loaded the metrics')
