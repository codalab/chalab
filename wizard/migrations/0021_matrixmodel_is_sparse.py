# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-26 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0020_auto_20160826_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='matrixmodel',
            name='is_sparse',
            field=models.BooleanField(default=False),
        ),
    ]
