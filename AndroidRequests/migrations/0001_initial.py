# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
            ],
        ),
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registrationPlate', models.CharField(max_length=8)),
                ('service', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='BusStop',
            fields=[
                ('longitud', models.FloatField(verbose_name=b'Longitude')),
                ('latitud', models.FloatField(verbose_name=b'Latitude')),
                ('code', models.CharField(max_length=6, serialize=False, verbose_name=b'Code', primary_key=True)),
                ('name', models.CharField(max_length=70, verbose_name=b'Name')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DevicePositionInTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField(verbose_name=b'Longitude')),
                ('latitud', models.FloatField(verbose_name=b'Latitude')),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
                ('userId', models.UUIDField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.CharField(max_length=8, serialize=False, verbose_name=b'Identifier', primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'Name')),
                ('description', models.CharField(max_length=140, null=True, verbose_name=b'Description')),
                ('lifespam', models.IntegerField(default=30, verbose_name=b'Lifespan')),
                ('category', models.CharField(max_length=20, verbose_name=b'Category')),
                ('origin', models.CharField(default=b'o', max_length=1, verbose_name=b'Origin', choices=[(b'i', b'the event was taken inside the bus'), (b'o', b'the event was taken from a bustop')])),
                ('eventType', models.CharField(max_length=7, verbose_name=b'Event Type', choices=[(b'bus', b'An event for the bus.'), (b'busStop', b'An event for the busStop.')])),
            ],
        ),
        migrations.CreateModel(
            name='EventForBus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
                ('timeCreation', models.DateTimeField(verbose_name=b'Creation Time')),
                ('eventConfirm', models.IntegerField(default=1, verbose_name=b'Confirmations')),
                ('eventDecline', models.IntegerField(default=0, verbose_name=b'Declines')),
                ('userId', models.UUIDField()),
                ('bus', models.ForeignKey(verbose_name=b'the bus', to='AndroidRequests.Bus')),
                ('event', models.ForeignKey(verbose_name=b'The event information', to='AndroidRequests.Event')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventForBusStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
                ('timeCreation', models.DateTimeField(verbose_name=b'Creation Time')),
                ('eventConfirm', models.IntegerField(default=1, verbose_name=b'Confirmations')),
                ('eventDecline', models.IntegerField(default=0, verbose_name=b'Declines')),
                ('userId', models.UUIDField()),
                ('aditionalInfo', models.CharField(default=b'nothing', max_length=140, verbose_name=b'Additional Information')),
                ('busStop', models.ForeignKey(verbose_name=b'Bus Stop', to='AndroidRequests.BusStop')),
                ('event', models.ForeignKey(verbose_name=b'The event information', to='AndroidRequests.Event')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NearByBusesLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
                ('userId', models.UUIDField()),
                ('busStop', models.ForeignKey(verbose_name=b'Bus Stop', to='AndroidRequests.BusStop')),
            ],
        ),
        migrations.CreateModel(
            name='PoseInTrajectoryOfToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField(verbose_name=b'Longitude')),
                ('latitud', models.FloatField(verbose_name=b'Latitude')),
                ('timeStamp', models.DateTimeField(db_index=True)),
                ('inVehicleOrNot', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeStamp', models.DateTimeField(db_index=True)),
                ('message', models.TextField()),
                ('imageName', models.CharField(default=b'no image', max_length=100)),
                ('reportInfo', models.TextField()),
                ('userId', models.UUIDField()),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField(verbose_name=b'Longitude')),
                ('latitud', models.FloatField(verbose_name=b'Latitude')),
                ('serviceCode', models.CharField(max_length=11, db_index=True)),
                ('sequence', models.IntegerField(verbose_name=b'Sequence')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('service', models.CharField(max_length=5, serialize=False, verbose_name=b'Service', primary_key=True)),
                ('origin', models.CharField(max_length=100)),
                ('destiny', models.CharField(max_length=100)),
                ('color', models.CharField(default=b'#00a0f0', max_length=7)),
                ('color_id', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField(verbose_name=b'Longitude')),
                ('latitud', models.FloatField(verbose_name=b'Latitude')),
                ('service', models.CharField(max_length=6, verbose_name=b'Service Code')),
                ('distance', models.IntegerField(verbose_name=b'Route Distance')),
            ],
        ),
        migrations.CreateModel(
            name='ServicesByBusStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=6)),
                ('busStop', models.ForeignKey(verbose_name=b'the busStop', to='AndroidRequests.BusStop')),
                ('service', models.ForeignKey(verbose_name=b'the service', to='AndroidRequests.Service')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceStopDistance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.CharField(max_length=6, verbose_name=b'Service Code')),
                ('distance', models.IntegerField(verbose_name=b'Distance Traveled')),
                ('busStop', models.ForeignKey(verbose_name=b'Bus Stop', to='AndroidRequests.BusStop')),
            ],
        ),
        migrations.CreateModel(
            name='StadisticDataFromRegistrationBus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField(verbose_name=b'Longitude')),
                ('latitud', models.FloatField(verbose_name=b'Latitude')),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
                ('confirmDecline', models.CharField(max_length=10, verbose_name=b'Confirm - Decline')),
                ('userId', models.UUIDField()),
                ('reportOfEvent', models.ForeignKey(verbose_name=b'Bus Event', to='AndroidRequests.EventForBus')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StadisticDataFromRegistrationBusStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField(verbose_name=b'Longitude')),
                ('latitud', models.FloatField(verbose_name=b'Latitude')),
                ('timeStamp', models.DateTimeField(verbose_name=b'Time Stamp')),
                ('confirmDecline', models.CharField(max_length=10, verbose_name=b'Confirm - Decline')),
                ('userId', models.UUIDField()),
                ('reportOfEvent', models.ForeignKey(verbose_name=b'Bus Stop Event', to='AndroidRequests.EventForBusStop')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('token', models.CharField(max_length=128, serialize=False, verbose_name=b'Token', primary_key=True)),
                ('direction', models.CharField(max_length=1, null=True)),
                ('color', models.CharField(default=b'#00a0f0', max_length=7, verbose_name=b"Icon's color")),
                ('userId', models.UUIDField()),
                ('bus', models.ForeignKey(verbose_name=b'Bus', to='AndroidRequests.Bus')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='servicelocation',
            index_together=set([('service', 'distance')]),
        ),
        migrations.AddField(
            model_name='service',
            name='busStops',
            field=models.ManyToManyField(to='AndroidRequests.BusStop', verbose_name=b'Bus Stops', through='AndroidRequests.ServicesByBusStop'),
        ),
        migrations.AddField(
            model_name='poseintrajectoryoftoken',
            name='token',
            field=models.ForeignKey(verbose_name=b'Token', to='AndroidRequests.Token'),
        ),
        migrations.AddField(
            model_name='busstop',
            name='events',
            field=models.ManyToManyField(to='AndroidRequests.Event', verbose_name=b'Events', through='AndroidRequests.EventForBusStop'),
        ),
        migrations.AddField(
            model_name='bus',
            name='events',
            field=models.ManyToManyField(to='AndroidRequests.Event', verbose_name=b'the event', through='AndroidRequests.EventForBus'),
        ),
        migrations.AddField(
            model_name='activetoken',
            name='token',
            field=models.OneToOneField(verbose_name=b'Token', to='AndroidRequests.Token'),
        ),
        migrations.AlterIndexTogether(
            name='poseintrajectoryoftoken',
            index_together=set([('token', 'timeStamp')]),
        ),
        migrations.AlterUniqueTogether(
            name='bus',
            unique_together=set([('registrationPlate', 'service')]),
        ),
    ]
