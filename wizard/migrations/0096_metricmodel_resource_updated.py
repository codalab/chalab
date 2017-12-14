# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-11 20:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0095_metricmodel_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='metricmodel',
            name='resource_updated',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
