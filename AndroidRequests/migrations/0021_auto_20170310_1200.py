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
        # Service model
        migrations.AddField(
            model_name='servicesbybusstop',
            name='service',
            field=models.ForeignKey(default=1, verbose_name=b'the service', to='AndroidRequests.Service'),
            preserve_default=False,
        ),
        # Token model
        migrations.AddField(
            model_name='poseintrajectoryoftoken',
            name='token',
            field=models.ForeignKey(default=1, verbose_name=b'Token', to='AndroidRequests.Token'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activetoken',
            name='token',
            field=models.OneToOneField(default=1, verbose_name=b'Token', to='AndroidRequests.Token'),
            preserve_default=False,
        ),
    ]
