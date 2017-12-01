# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-22 21:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0092_datasetmodel_raw_zip_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='columnardocdefinition',
            name='raw_content_original_name',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='columnarnamesdefinition',
            name='raw_content_original_name',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='columnartypesdefinition',
            name='raw_content_original_name',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='datasetmodel',
            name='resource_updated',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name='matrixmodel',
            name='raw_content_original_name',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='datasetmodel',
            name='resource_created',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
