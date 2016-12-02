# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0009_auto_20161013_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stadisticdatafromregistrationbus',
            name='reportOfEvent',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbus',
            old_name='reportOfEventv2',
            new_name='reportOfEvent',
        ),
        migrations.AlterField(
            model_name='stadisticdatafromregistrationbus',
            name='reportOfEvent',
            field=models.ForeignKey(
                verbose_name=b'Bus Event',
                to='AndroidRequests.EventForBusv2',
                null=False),
        ),
    ]
