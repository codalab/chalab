from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from wizard.models import DatasetModel, MetricModel, ChallengeModel

palette = ['81c784', 'ffb64c', '4cb5ab', 'b967c7',
           'ef6191', '7884cb', 'dce674', 'a1877e', 'f77b71']


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

    base_challenge = models.ForeignKey(ChallengeModel, null=True)

    def __str__(self):
        admin = self.admins.first()
        return "Group '%s' by %s" % (self.name, admin)

    def get_absolute_url(self):
        return reverse('group:edit', kwargs={'group_id': self.id})

    def get_color(self):
        return palette[self.id % len(palette)]
