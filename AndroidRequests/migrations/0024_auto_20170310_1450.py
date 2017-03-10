# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

"""
-- make uniques 
"""

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0023_auto_20170310_1529'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='busstop',
            unique_together=set([('code', 'gtfs')]),
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('serviceCode', 'sequence', 'gtfs')]),
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('service', 'gtfs')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicelocation',
            unique_together=set([('service', 'distance', 'gtfs')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicesbybusstop',
            unique_together=set([('code', 'busStop', 'gtfs')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicestopdistance',
            unique_together=set([('busStop', 'service', 'gtfs')]),
        ),
    ]
