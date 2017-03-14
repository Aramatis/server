# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import F
from django.db import models, migrations

"""
PROCEDURE
- Insert data on column
"""

def fullData(apps, schema_editor):
    ''' '''
    servicesbybusstopM = apps.get_model('AndroidRequests', 'servicesbybusstop')
    servicesbybusstopM.objects.all().update(busStop_id=F('busStop_id_aux'))

    servicestopdistanceM = apps.get_model('AndroidRequests', 'servicestopdistance')
    servicestopdistanceM.objects.all().update(busStop_id=F('busStop_id_aux'))

    eventforbusstopM = apps.get_model('AndroidRequests', 'eventforbusstop')
    eventforbusstopM.objects.all().update(busStop_id=F('busStop_id_aux'))

    # Service model
    servicesbybusstopM = apps.get_model('AndroidRequests', 'servicesbybusstop')
    servicesbybusstopM.objects.all().update(service_id=F('service_id_aux'))

    # Token model
    trajectoryM = apps.get_model('AndroidRequests', 'poseintrajectoryoftoken')
    trajectoryM.objects.all().update(token_id=F('token_id_aux'))

    activetokenM = apps.get_model('AndroidRequests', 'activetoken')
    activetokenM.objects.all().update(token_id=F('token_id_aux'))


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0021_auto_20170310_1200'),
    ]

    operations = [
        # full foreign key
        migrations.RunPython(fullData),
    ]
