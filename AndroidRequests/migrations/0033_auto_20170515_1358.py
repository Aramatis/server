# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0032_auto_20170509_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventforbusstop',
            name='broken',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='eventforbusstop',
            name='brokenType',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='eventforbusv2',
            name='broken',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='eventforbusv2',
            name='brokenType',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
    ]
