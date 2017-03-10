# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import F
from django.db import models, migrations

"""
PROCEDURE
- Add foreign key
"""

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0020_auto_20170310_1135'),
    ]

    operations = [
        # add foreign key
        migrations.AddField(
            model_name='servicesbybusstop',
            name='busStop',
            field=models.ForeignKey(default=1, verbose_name=b'the busStop', to='AndroidRequests.BusStop'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicestopdistance',
            name='busStop',
            field=models.ForeignKey(default=1, verbose_name=b'Bus Stop', to='AndroidRequests.BusStop'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventforbusstop',
            name='busStop',
            field=models.ForeignKey(default=1, verbose_name=b'Bus Stop', to='AndroidRequests.BusStop'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nearbybuseslog',
            name='busStop',
            field=models.ForeignKey(default=1, verbose_name=b'Bus Stop', to='AndroidRequests.BusStop'),
            preserve_default=False,
        ),
        # for service model
        migrations.AddField(
            model_name='servicesbybusstop',
            name='service',
            field=models.ForeignKey(default=1, verbose_name=b'the service', to='AndroidRequests.Service'),
            preserve_default=False,
        ),
    ]
