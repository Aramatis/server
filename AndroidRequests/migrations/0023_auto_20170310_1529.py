# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import F
from django.db import models, migrations

"""
PROCEDURE
- Delete aux column
"""

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0022_auto_20170310_1525'),
    ]

    operations = [
        # remove aux columns
        migrations.RemoveField(
            model_name='servicesbybusstop',
            name='busStop_id_aux',
        ),
        migrations.RemoveField(
            model_name='servicestopdistance',
            name='busStop_id_aux',
        ),
        migrations.RemoveField(
            model_name='eventforbusstop',
            name='busStop_id_aux',
        ),
        migrations.RemoveField(
            model_name='nearbybuseslog',
            name='busStop_id_aux',
        ),
        migrations.RemoveField(
            model_name='servicesbybusstop',
            name='service_id_aux',
        ),

    ]
