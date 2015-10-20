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
                ('timeStamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='DevicePositionInTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField()),
                ('latitud', models.FloatField()),
                ('timeStamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PoseInTrajectoryOfToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longitud', models.FloatField()),
                ('latitud', models.FloatField()),
                ('timeStamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('tokenID', models.CharField(max_length=128, serialize=False, primary_key=True)),
                ('busService', models.CharField(max_length=5)),
                ('busRegistrationPlate', models.CharField(max_length=8)),
                ('color', models.CharField(default=b'#00a0f0', max_length=7)),
            ],
        ),
        migrations.AddField(
            model_name='poseintrajectoryoftoken',
            name='token',
            field=models.ForeignKey(to='AndroidRequests.Token'),
        ),
        migrations.AddField(
            model_name='activetoken',
            name='token',
            field=models.ForeignKey(to='AndroidRequests.Token'),
        ),
    ]
