# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-25 17:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('licensePlate', models.CharField(max_length=7, null=True)),
                ('serviceName', models.CharField(max_length=7, null=True)),
                ('timeMessage', models.CharField(max_length=50, null=True)),
                ('valid', models.CharField(max_length=1, null=False)),
                ('distance', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('busStopCode', models.CharField(max_length=6)),
                ('serverTimeStamp', models.DateTimeField()),
                ('dtpmTimeStamp', models.DateTimeField()),
                ('webTransId', models.CharField(db_index=True, max_length=24)),
                ('errorMessage', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='buslog',
            name='log',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PredictorDTPM.Log'),
        ),
    ]
