# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-17 18:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0043_auto_20171117_1539'),
        ('gtfs', '0001_initial')
    ]

    state_operations = [
        migrations.AlterField(
            model_name='NearByBusesLog',
            name='busStop',
            field = models.ForeignKey(verbose_name=b'Bus Stop', to='gtfs.BusStop')
        )
    ]

    operations = [
       migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
