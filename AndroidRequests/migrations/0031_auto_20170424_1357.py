# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0030_auto_20170421_1835'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbus',
            old_name='gpsLatitud',
            new_name='gpsLatitude',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbus',
            old_name='gpsLongitud',
            new_name='gpsLongitude',
        ),
    ]
