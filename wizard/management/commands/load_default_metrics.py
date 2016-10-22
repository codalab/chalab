import logging

from django.core.management.base import BaseCommand

from wizard import models

log = logging.getLogger('wizard.commands.load_default_metrics')

METRICS = {
    'bac_metric': {
        'description': """Normalized balanced accuracy""",
        'is_default': True,
        'classification': True
    },
    'pac_metric': {
        'description': """Probabilistic Accuracy based on log_loss""",
        'is_default': True,
        'classification': True
    },
    'f1_metric': {
        'description': """Normalized f1 measure""",
        'is_default': True,
        'classification': True
    },
    'auc_metric': {
        'description': """Normalized Area under ROC curve""",
        'is_default': True,
        'classification': True
    },

    'r2_metric': {
        'description': """Mean squared error divided by variance""",
        'is_default': True,
        'regression': True
    },
    'a_metric': {
        'description': """Mean absolute error divided by mean absolute deviation""",
        'is_default': True,
        'regression': True
    },
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
                is_default=content.get('is_default', False),
                classification=content.get('classification', False),
                regression=content.get('regression', False),
            )
            self._success('Successfully loaded metric: %s' % name)

        self._success('Successfully loaded the metrics')
