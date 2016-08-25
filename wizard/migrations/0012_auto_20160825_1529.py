# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-25 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0011_matrixmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matrixmodel',
            name='columns',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='matrix_cols', to='wizard.AxisDescriptionModel'),
        ),
        migrations.AlterField(
            model_name='matrixmodel',
            name='rows',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='matrix_rows', to='wizard.AxisDescriptionModel'),
        ),
    ]
