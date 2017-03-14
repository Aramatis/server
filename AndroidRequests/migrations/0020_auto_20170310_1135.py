# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import F
from django.db import models, migrations

"""
PROCEDURE
- Remove foreign key 
- Change primary key
"""

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
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
        # Service model
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
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
        # Token model
        migrations.RemoveField(
            model_name='poseintrajectoryoftoken',
            name='token'
        ),
        migrations.RemoveField(
            model_name='activetoken',
            name='token'
        ),
        migrations.AlterField(
            model_name='token',
            name='token',
            field=models.CharField(max_length=128, verbose_name=b'Token'),
        ),
        migrations.AlterField(
            model_name='token',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
    ]
