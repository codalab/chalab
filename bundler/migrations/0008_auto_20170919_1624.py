# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-19 16:24
from __future__ import unicode_literals

import bundler.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bundler', '0007_auto_20170615_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bundletaskmodel',
            name='challenge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bundle_tasks', to='wizard.ChallengeModel'),
        ),
        migrations.AlterField(
            model_name='bundletaskmodel',
            name='output',
            field=models.FileField(null=True, upload_to=bundler.models.StorageNameFactory('bundle')),
        ),
    ]