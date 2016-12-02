# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0016_auto_20161110_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='stadisticdatafromregistrationbus',
            name='distance',
            field=models.FloatField(null=True, verbose_name=b'Distance'),
        ),
        migrations.AddField(
            model_name='stadisticdatafromregistrationbus',
            name='gpsLatitud',
            field=models.FloatField(null=True, verbose_name=b'GPS Latitude'),
        ),
        migrations.AddField(
            model_name='stadisticdatafromregistrationbus',
            name='gpsLongitud',
            field=models.FloatField(null=True, verbose_name=b'GPS Longitude'),
        ),
        migrations.AddField(
            model_name='stadisticdatafromregistrationbus',
            name='gpsTimeStamp',
            field=models.DateTimeField(
                null=True, verbose_name=b'GPS Time Stamp'),
        ),
    ]
