from django.db import models

from wizard.models import ChallengeModel


class LogModel(models.Model):
    DEBUG = 0
    INFO = 10
    WARNING = 20
    ERROR = 30
    CRITICAL = 40

    task = models.ForeignKey('BundleTaskModel', null=False, related_name='log')

    created = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField()
    message = models.TextField()


class BundleTaskModel(models.Model):
    SCHEDULED = "scheduled"
    STARTED = "started"
    CANCELLED = "cancelled"
    FINISHED = "finished"

    STATE_CHOICES = (
        (SCHEDULED, "Scheduled"),
        (STARTED, "Started"),
        (CANCELLED, "Cancelled"),
        (FINISHED, "Finished")
    )

    challenge = models.ForeignKey(ChallengeModel, null=False)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    progress_perc = models.IntegerField(default=0, null=False)

    created = models.DateTimeField(auto_now_add=True)
    closed = models.DateTimeField(null=True)

    output = models.FileField(null=True)

    def do_log(self, message, level=LogModel.INFO):
        return LogModel.objects.create(task=self, level=level, message=message)
