import logging

from django.core.management.base import BaseCommand

from wizard import models

log = logging.getLogger('wizard.commands.load_default_metrics')

METRICS = {
    'bac_binary': {'description': """Normalized balanced accuracy for binary data""",
                   'is_default': True,
                   'classification': True,
                   },
    'bac_multiclass': {'description': """Normalized balanced accuracy for multi-class data""",
                       'is_default': True,
                       'classification': True,
                       },
    'bac_multilabel': {'description': """Normalized balanced accuracy for multi-labeled data""",
                       'is_default': True,
                       'classification': True,
                       },
    'auc_binary': {'description': """Normalized Area under ROC curve for binary data""",
                   'is_default': True,
                   'classification': True,
                   },
    'auc_multilabel': {'description': """Normalized Area under ROC curve for multi-labeled data""",
                       'is_default': True,
                       'classification': True,
                       },
    'pac_binary': {'description': """Probabilistic Accuracy based on log_loss for binary data""",
                   'is_default': True,
                   'classification': True,
                   },
    'pac_multiclass': {
        'description': """Probabilistic Accuracy based on log_loss for multi-class data""",
        'is_default': True,
        'classification': True,
    },
    'pac_multilabel': {
        'description': """Probabilistic Accuracy based on log_loss for multi-label data""",
        'is_default': True,
        'classification': True,
    },
    'f1_binary': {'description': """Normalized f1 measure for binary data""",
                  'is_default': True,
                  'classification': True,
                  },
    'f1_multilabel': {'description': """Normalized f1 measure for multi-labeled data""",
                      'is_default': True,
                      'classification': True,
                      },
    'abs_regression': {'description': """Mean absolute error divided by mean absolute deviation""",
                       'is_default': True,
                       'regression': True
                       },
    'r2_regression': {'description': """Mean squared error divided by variance""",
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
        #self._warn("This command is designed to be run only once.\n"
        #           "You need to remove previous metrics by hand.")

        # Verify if we already have some MetricModel
        if models.MetricModel.objects.exists() :
            self._warn("Database already initialised, skipping initialization.")
        else:
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
                    description=content.get("description", None)
                )
                self._success('Successfully loaded metric: %s' % name)

        self._success('Successfully loaded the metrics')
