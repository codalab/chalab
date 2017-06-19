# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-15 19:01
from __future__ import unicode_literals

import chalab.tools.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0074_auto_20170615_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baselinemodel',
            name='submission',
            field=models.FileField(blank=True, null=True, upload_to=chalab.tools.storage.save_to_baseline, verbose_name='baseline submission'),
        ),
    ]
