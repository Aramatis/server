# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import AndroidRequests.constants as Constants

def fill_tables(apps, schema_editor):
    # tokens = apps.get_model('AndroidRequests', 'token')
    # for token in MyModel.objects.all():
    #     token.uuid = uuid.uuid4()
    #     token.save()
    #migrate data from Bus to Busv2 and Busassignment
    buses = apps.get_model('AndroidRequests', 'bus')
    busesv2 = apps.get_model('AndroidRequests', 'busv2')
    busesassignments = apps.get_model('AndroidRequests', 'busassignment')
    uuidsArray = {}
    service_plate_array = []
    for bus in buses.objects.all():
        pUUID = None
        if bus.registrationPlate.upper() == Constants.DUMMY_LICENSE_PLATE:
            busesv2(
                registrationPlate = bus.registrationPlate.upper(),
                uuid = bus.uuid
                ).save()
            pUUID = bus.uuid
        elif bus.registrationPlate.upper() in uuidsArray:
            pUUID = uuidsArray[bus.registrationPlate.upper()]
        else:
            uuidsArray[bus.registrationPlate.upper()] = bus.uuid
            busesv2(
                registrationPlate = bus.registrationPlate.upper(),
                uuid = bus.uuid
                ).save()
            pUUID = uuidsArray[bus.registrationPlate.upper()]  
        if (bus.registrationPlate.upper() == Constants.DUMMY_LICENSE_PLATE) or \
                ([bus.registrationPlate.upper(), bus.service] not in service_plate_array): 
            busesassignments(
                service = bus.service,
                uuid = busesv2.objects.get(uuid = pUUID)
                ).save()
            if bus.registrationPlate.upper() != Constants.DUMMY_LICENSE_PLATE:
                service_plate_array.append([bus.registrationPlate.upper(), bus.service])
    #migrate data from Event4Bus to E4Bv2
    eventsforbuses = apps.get_model('AndroidRequests','eventforbus')
    eventsforbusesv2 =  apps.get_model('AndroidRequests','eventforbusv2')
    for eventforbus in eventsforbuses.objects.all():
        busv2 = None
        if eventforbus.bus.registrationPlate.upper() == Constants.DUMMY_LICENSE_PLATE:
            busv2 = busesv2.objects.get(uuid = eventforbus.bus.uuid)
        else:
            busv2 = busesv2.objects.get(registrationPlate = buses.objects.get(id = eventforbus.bus_id).registrationPlate.upper())
        eventsforbusesv2(  
            ex_id = eventforbus.id,
            timeStamp = eventforbus.timeStamp,
            timeCreation = eventforbus.timeCreation,
            eventConfirm = eventforbus.eventConfirm,
            eventDecline = eventforbus.eventDecline,
            userId = eventforbus.userId,
            busassignment = busesassignments.objects.get(uuid = busv2, service = eventforbus.bus.service),
            event = eventforbus.event,
            ).save()

    tokens = apps.get_model('AndroidRequests', 'token')
    for token in tokens.objects.all():
        bus = buses.objects.get(id = token.bus_id)
        busv2 = None
        if bus.registrationPlate.upper() == Constants.DUMMY_LICENSE_PLATE:
            busv2 = busesv2.objects.get(uuid = bus.uuid)            
        else:
            busv2 = busesv2.objects.get(registrationPlate = bus.registrationPlate.upper() )
        token.busassignment = busesassignments.objects.get(uuid = busv2, service = token.bus.service)
        token.save()
    


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0007_auto_20160928_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='Busassignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Busv2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registrationPlate', models.CharField(max_length=8)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventForBusv2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
                ('timeCreation', models.DateTimeField(verbose_name=b'Creation Time')),
                ('eventConfirm', models.IntegerField(default=1, verbose_name=b'Confirmations')),
                ('eventDecline', models.IntegerField(default=0, verbose_name=b'Declines')),
                ('userId', models.UUIDField()),
                ('busassignment', models.ForeignKey(verbose_name=b'the bus', to='AndroidRequests.Busassignment')),
                ('event', models.ForeignKey(verbose_name=b'The event information', to='AndroidRequests.Event')),
                ('ex_id', models.IntegerField(default=0, verbose_name=b'old eventforbus id', unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='token',
            name='busassignment',
            field=models.ForeignKey(verbose_name=b'Bus', to='AndroidRequests.Busassignment', null = True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='busassignment',
            name='events',
            field=models.ManyToManyField(to='AndroidRequests.Event', verbose_name=b'the event', through='AndroidRequests.EventForBusv2'),
        ),
        migrations.AddField(
            model_name='busassignment',
            name='uuid',
            field=models.ForeignKey(verbose_name=b'Thebusv2', to='AndroidRequests.Busv2'),
        ),
        #run  function to fill the new tables
        migrations.RunPython(fill_tables, reverse_code=migrations.RunPython.noop),

        migrations.RemoveField(
            model_name='token',
            name='bus',
        ),
        migrations.RemoveField(
            model_name='token',
            name='uuid',
        ),        
        migrations.AlterField(
            model_name='token',
            name='busassignment',
            field=models.ForeignKey(verbose_name=b'Bus', to='AndroidRequests.Busassignment', null = False),
            preserve_default=False,
        ),
    ]
