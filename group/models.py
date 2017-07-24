from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from wizard.models import DatasetModel, MetricModel

palette = ['81c784', 'ffb64c', '4cb5ab', 'b967c7',
           'ef6191', '7884cb', 'dce674', 'a1877e', 'f77b71']

class GroupModel(models.Model):
    admins = models.ManyToManyField(User, db_table='admin_group',
                                    related_name='admin_of_group')

    users = models.ManyToManyField(User, db_table='user_group',
                                   related_name='user_of_group')

    name = models.CharField(max_length=30, null=False, default='new group')

    default_dataset = models.ManyToManyField(DatasetModel,
                                             db_table='dataset_group')

    default_metric = models.ManyToManyField(MetricModel,
                                            db_table='metric_group')

    def get_absolute_url(self):
        return reverse('group:edit', kwargs={'group_id': self.id})

    def get_color(self):
        return palette[self.id % len(palette)]
