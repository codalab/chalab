# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-29 13:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0060_auto_20161029_0847'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaselineModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='challengemodel',
            name='baseline',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='challenge', to='wizard.BaselineModel'),
        ),
    ]