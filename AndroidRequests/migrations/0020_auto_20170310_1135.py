# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import F
from django.db import models, migrations

"""
PROCEDURE
- Remove foreign key 
- Change primary key in bus stop model
"""

def fullData(apps, schema_editor):
    ''' '''
    servicesbybusstopM = apps.get_model('AndroidRequests', 'servicesbybusstop')
    servicesbybusstopM.objects.all().update(busStop_id=F('busStop_id_aux'))

    servicestopdistanceM = apps.get_model('AndroidRequests', 'servicestopdistance')
    servicestopdistanceM.objects.all().update(busStop_id=F('busStop_id_aux'))

    eventforbusstopM = apps.get_model('AndroidRequests', 'eventforbusstop')
    eventforbusstopM.objects.all().update(busStop_id=F('busStop_id_aux'))

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0019_auto_20170310_1059'),
    ]

    operations = [
        # remove foreign key
        migrations.RemoveField(
            model_name='servicesbybusstop',
            name='busStop'
        ),
        migrations.RemoveField(
            model_name='servicestopdistance',
            name='busStop'
        ),
        migrations.RemoveField(
            model_name='eventforbusstop',
            name='busStop'
        ),
        migrations.RemoveField(
            model_name='nearbybuseslog',
            name='busStop'
        ),
        # make code field not primary key 
        migrations.AlterField(
            model_name='busstop',
            name='code',
            field=models.CharField(max_length=6, verbose_name=b'Code'),
        ),
        # make id field primary key
        migrations.AlterField(
            model_name='busstop',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True),
        ),
        # for service model
        migrations.RemoveField(
            model_name='servicesbybusstop',
            name='service'
        ),
        # make service field not primary key 
        migrations.AlterField(
            model_name='service',
            name='service',
            field=models.CharField(max_length=11, verbose_name=b'Service'),
        ),
        # make id field primary key
        migrations.AlterField(
            model_name='service',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True),
        ),
    ]
