# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-20 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bundler', '0008_auto_20170919_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='bundletaskmodel',
            name='current_task_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
