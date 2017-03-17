# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils import timezone

GTFS_ID=1

def addFirstVersion(apps, schema_editor):
    """ add first gtfs version """
    gtfs = apps.get_model('AndroidRequests', 'gtfs')
    #gtfs.objects.create(id=GTFS_ID, version='v0.6', timeCreation=timezone.now())
    gtfs.objects.create(version='v0.6', timeCreation=timezone.now())

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0017_auto_20161123_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='GTFS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(default=None, unique=True, max_length=10)),
                ('timeCreation', models.DateTimeField(null=True, verbose_name=b'Time Creation')),
            ],
        ),
        migrations.RunPython(addFirstVersion),
        migrations.AddField(
            model_name='token',
            name='timeCreation',
            field=models.DateTimeField(null=True, verbose_name=b'Time Creation'),
        ),
        migrations.AddField(
            model_name='busstop',
            name='gtfs',
            field=models.ForeignKey(default=GTFS_ID, verbose_name=b'gtfs version', to='AndroidRequests.GTFS'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='route',
            name='gtfs',
            field=models.ForeignKey(default=GTFS_ID, verbose_name=b'gtfs version', to='AndroidRequests.GTFS'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='service',
            name='gtfs',
            field=models.ForeignKey(default=GTFS_ID, verbose_name=b'gtfs version', to='AndroidRequests.GTFS'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicelocation',
            name='gtfs',
            field=models.ForeignKey(default=GTFS_ID, verbose_name=b'gtfs version', to='AndroidRequests.GTFS'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicesbybusstop',
            name='gtfs',
            field=models.ForeignKey(default=GTFS_ID, verbose_name=b'gtfs version', to='AndroidRequests.GTFS'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicestopdistance',
            name='gtfs',
            field=models.ForeignKey(default=GTFS_ID, verbose_name=b'gtfs version', to='AndroidRequests.GTFS'),
            preserve_default=False,
        ),
    ]
