# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0017_auto_20161123_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='GtfsVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gtfsVersion', models.CharField(default=None, unique=True, max_length=10)),
                ('timeCreation', models.DateTimeField(null=True, verbose_name=b'Time Creation')),
            ],
        ),
        migrations.AddField(
            model_name='token',
            name='timeCreation',
            field=models.DateTimeField(null=True, verbose_name=b'Time Creation'),
        ),
        migrations.AddField(
            model_name='busstop',
            name='gtfsVersion',
            field=models.ForeignKey(default='v0.6', verbose_name=b'gtfs version', to='AndroidRequests.GtfsVersion'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='route',
            name='gtfsVersion',
            field=models.ForeignKey(default='v0.6', verbose_name=b'gtfs version', to='AndroidRequests.GtfsVersion'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='service',
            name='gtfsVersion',
            field=models.ForeignKey(default='v0.6', verbose_name=b'gtfs version', to='AndroidRequests.GtfsVersion'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicelocation',
            name='gtfsVersion',
            field=models.ForeignKey(default='v0.6', verbose_name=b'gtfs version', to='AndroidRequests.GtfsVersion'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicesbybusstop',
            name='gtfsVersion',
            field=models.ForeignKey(default='v0.6', verbose_name=b'gtfs version', to='AndroidRequests.GtfsVersion'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicestopdistance',
            name='gtfsVersion',
            field=models.ForeignKey(default='v0.6', verbose_name=b'gtfs version', to='AndroidRequests.GtfsVersion'),
            preserve_default=False,
        ),
    ]
