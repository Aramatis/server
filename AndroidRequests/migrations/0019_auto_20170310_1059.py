# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

"""
PROCEDURE
- Create id column for busStop model
- Create aux id column for servicesbybusstop, servicestopdistance, eventforbusstop, nearbybuseslog models
- Assign bus stop id
- Assign bus stop id to aux id columns
"""

def assignBusStopId(apps, schema_editor):
    ''' '''
    busStopM = apps.get_model('AndroidRequests', 'busStop')

    busStopId = 1
    for busstop in busStopM.objects.all():
        busstop.id = busStopId
        busstop.save()
        busStopId +=1
    print "Finish to add ids to bus stop records"

def assignServiceId(apps, schema_editor):
    ''' '''
    serviceM = apps.get_model('AndroidRequests', 'service')

    serviceId = 1
    for service in serviceM.objects.all():
        service.id = serviceId
        service.save()
        serviceId +=1
    print "Finish to add ids to service records"

def assignTokenId(apps, schema_editor):
    ''' '''
    tokenM = apps.get_model('AndroidRequests', 'token')

    tokenId = 1
    for token in tokenM.objects.all():
        token.id = tokenId
        token.save()
        tokenId +=1
    print "Finish to add ids to token records"

def changeServicesbybusstop(apps, schema_editor):
    ''' '''
    busStopM = apps.get_model('AndroidRequests', 'busstop')
    servicesbybusstopM = apps.get_model('AndroidRequests', 'servicesbybusstop')
    for busstop in busStopM.objects.all():
        servicesbybusstopM.objects.filter(busStop=busstop).update(busStop_id_aux=busstop.id)
    print "Finish..."

def changeServicestopdistance(apps, schema_editor):
    ''' '''
    busStopM = apps.get_model('AndroidRequests', 'busStop')
    servicestopdistanceM = apps.get_model('AndroidRequests', 'servicestopdistance')
    for busstop in busStopM.objects.all():
        servicestopdistanceM.objects.filter(busStop=busstop).update(busStop_id_aux=busstop.id)
    print "Finish..."

def changeEventforbusstop(apps, schema_editor):
    ''' '''
    busStopM = apps.get_model('AndroidRequests', 'busStop')
    eventforbusstopM = apps.get_model('AndroidRequests', 'eventforbusstop')
    for busstop in busStopM.objects.all():
        eventforbusstopM.objects.filter(busStop=busstop).update(busStop_id_aux=busstop.id)
    print "Finish..."

def changeNearbybuseslog(apps, schema_editor):
    ''' '''
    busStopM = apps.get_model('AndroidRequests', 'busStop')
    nearbybuseslogM = apps.get_model('AndroidRequests', 'nearbybuseslog')
    for busstop in busStopM.objects.all():
        nearbybuseslogM.objects.filter(busStop=busstop).update(busStop_id_aux=busstop.id)
    print "Finish..."

# service model
def changeServicesbybusstopService(apps, schema_editor):
    ''' '''
    serviceM = apps.get_model('AndroidRequests', 'service')
    servicesbybusstopM = apps.get_model('AndroidRequests', 'servicesbybusstop')
    for service in serviceM.objects.all():
        servicesbybusstopM.objects.filter(service=service).update(service_id_aux=service.id)
    print "Finish..."

# token model
def changePoseintrajectoryoftoken(apps, schema_editor):
    ''' '''
    tokenM = apps.get_model('AndroidRequests', 'token')
    trajectoryM = apps.get_model('AndroidRequests', 'poseintrajectoryoftoken')
    for token in tokenM.objects.all():
        trajectoryM.objects.filter(token=token).update(token_id_aux=token.id)
    print "Finish..."

def changeActivetoken(apps, schema_editor):
    ''' '''
    tokenM = apps.get_model('AndroidRequests', 'token')
    activetokenM = apps.get_model('AndroidRequests', 'activetoken')
    for token in tokenM.objects.all():
        activetokenM.objects.filter(token=token).update(token_id_aux=token.id)
    print "Finish..."


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0018_auto_20161220_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='busstop',
            name='id',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicesbybusstop',
            name='busStop_id_aux',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicestopdistance',
            name='busStop_id_aux',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventforbusstop',
            name='busStop_id_aux',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nearbybuseslog',
            name='busStop_id_aux',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        # service model
        migrations.AddField(
            model_name='service',
            name='id',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicesbybusstop',
            name='service_id_aux',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        # token model
        migrations.AddField(
            model_name='token',
            name='id',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='poseintrajectoryoftoken',
            name='token_id_aux',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activetoken',
            name='token_id_aux',
            field=models.IntegerField(default=-1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        # busstop model
        migrations.RunPython(assignBusStopId),
        migrations.RunPython(changeServicesbybusstop),
        migrations.RunPython(changeServicestopdistance),
        migrations.RunPython(changeEventforbusstop),
        migrations.RunPython(changeNearbybuseslog),
        # service model
        migrations.RunPython(assignServiceId),
        migrations.RunPython(changeServicesbybusstopService),
        # token model
        migrations.RunPython(assignTokenId),
        migrations.RunPython(changePoseintrajectoryoftoken),
        migrations.RunPython(changeActivetoken),
    ]
