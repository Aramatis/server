# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid

def fill_tables(apps, schema_editor):
    # tokens = apps.get_model('AndroidRequests', 'token')
    # for token in MyModel.objects.all():
    #     token.uuid = uuid.uuid4()
    #     token.save()
    #migrate data from Bus to Busv2 and Busassignment
    buses = apps.get_model('AndroidRequests', 'bus')
    busesv2 = apps.get_model('AndroidRequests', 'busv2')
    busesassignments = apps.get_model('AndroidRequests', 'busassignment')
    for bus in buses.objects.all():
        busesv2(
            registrationPlate = bus.registrationPlate,
            uuid = bus.uuid
            ).save()

        busesassignments(
            service = bus.service,
            uuid = busesv2.objects.get(uuid = bus.uuid)
            ).save()
    #migrate data from Event4Bus to E4Bv2
    eventsforbuses = apps.get_model('AndroidRequests','eventforbus')
    eventsforbusesv2 =  apps.get_model('AndroidRequests','eventforbusv2')
    for eventforbus in eventsforbuses.objects.all():
        busv2 = busesv2.objects.get(uuid = buses.objects.get(id = eventforbus.bus_id).uuid)
        eventsforbusesv2(
            timeStamp = eventforbus.timeStamp,
            timeCreation = eventforbus.timeCreation,
            eventConfirm = eventforbus.eventConfirm,
            eventDecline = eventforbus.eventDecline,
            userId = eventforbus.userId,
            busassignment = busesassignments.objects.get(uuid = busv2),
            event = eventforbus.event,
            ).save()

    tokens = apps.get_model('AndroidRequests', 'token')
    for token in tokens.objects.all():
        busv2 = busesv2.objects.get(uuid = buses.objects.get(id = token.bus_id).uuid)
        token.busassignment = busesassignments.objects.get(uuid = busv2)
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
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False)),
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
