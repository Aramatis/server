# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-26 15:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0050_report_transappuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='imageFile',
            field=models.FileField(default=None, null=True, upload_to=b'reported_images'),
        ),
    ]