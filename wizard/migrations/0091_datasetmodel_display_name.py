# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-16 21:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0090_auto_20171103_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetmodel',
            name='display_name',
            field=models.CharField(default='', max_length=256),
        ),
    ]
