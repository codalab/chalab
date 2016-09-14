from django.db import models

from wizard.models import ChallengeModel


class LogModel(models.Model):
    DEBUG = 0
    INFO = 10
    WARNING = 20
    ERROR = 30
    CRITICAL = 40

    task = models.ForeignKey('BundleTaskModel', null=False, related_name='log_set')

    created = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField()
    message = models.TextField()


class BundleTaskModel(models.Model):
    SCHEDULED = "scheduled"
    STARTED = "started"
    CANCELLED = "cancelled"
    FAILED = 'failed'
    FINISHED = "finished"

    STATE_CHOICES = (
        (SCHEDULED, "Scheduled"),
        (STARTED, "Started"),
        (CANCELLED, "Cancelled"),
        (FINISHED, "Finished"),
        (FAILED, 'Failed'),
    )

    challenge = models.ForeignKey(ChallengeModel, null=False)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    progress_perc = models.IntegerField(default=0, null=False)

    created = models.DateTimeField(auto_now_add=True)
    closed = models.DateTimeField(null=True)

    output = models.FileField(null=True)

    def __str__(self):
        return "<%s: challenge=%s, state=%s>" \
               % (type(self).__name__, self.challenge.title, self.get_state_display())

    def add_log(self, message, level=LogModel.INFO):
        return LogModel.objects.create(task=self, level=level, message=message)

    @property
    def is_download_ready(self):
        return self.state == self.FINISHED

    @classmethod
    def create(cls, challenge):
        return cls.objects.create(challenge=challenge,
                                  state=cls.SCHEDULED,
                                  closed=None,
                                  output=None)

    @property
    def done(self):
        return self.state in {self.FAILED, self.CANCELLED, self.FINISHED}

    @property
    def logs(self):
        return self.log_set.order_by('created').all()

    class Meta:
        ordering = ['-created']
