# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-23 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0047_token_purgetype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='purgeType',
            field=models.CharField(choices=[(b'user', b'user says get off'), (b'server', b'server says get off'), (b'cron_finished_trip', b'cron finished trip'), (b'phone_far_away', b'smartphone says that is far away from real bus'), (b'phone_still', b'smartphone says that there is not movement')], max_length=50, null=True),
        ),
    ]
