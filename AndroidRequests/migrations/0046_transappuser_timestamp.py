# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-21 21:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0045_auto_20171117_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='transappuser',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
