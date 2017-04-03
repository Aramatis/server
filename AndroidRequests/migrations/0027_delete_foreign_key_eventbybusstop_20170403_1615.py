# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

"""
PROCEDURE
- Delete foreign keys for eventforbusstop model
"""

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0026_auto_20170403_1424'),
    ]

    operations = [
        # eventforbusstop model
        migrations.RemoveField(
            model_name='busstop',
            name='events',
        ),
        migrations.RemoveField(
            model_name='eventforbusstop',
            name='busStop',
        ),
    ]
