from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from wizard.models import DatasetModel, MetricModel, ChallengeModel


class GroupModel(models.Model):
    admins = models.ManyToManyField(User, db_table='admin_group',
                                    related_name='admin_of_group')

    public = models.BooleanField(null=False, default=True)
    hidden = models.BooleanField(null=False, default=False)

    users = models.ManyToManyField(User, db_table='user_group', blank=True,
                                   related_name='user_of_group')

    name = models.CharField(max_length=30, null=False, default='New group')
    description = models.TextField(max_length=1000, null=False, blank=True, default='')

    default_dataset = models.ManyToManyField(DatasetModel, blank=True,
                                             db_table='dataset_group')

    default_metric = models.ManyToManyField(MetricModel, blank=True,
                                            db_table='metric_group')

    template = models.ForeignKey(ChallengeModel, null=True, blank=True)

    def __str__(self):
        admin = self.admins.first()
        return "%s group '%s' by %s" % ('Public' if self.public else 'Private', self.name, admin)

    def get_absolute_url(self):
        return reverse('group:edit', kwargs={'group_id': self.id})
