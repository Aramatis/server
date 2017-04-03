# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

"""
PROCEDURE
- Create stopCode column in eventforbusstop model
- Assign stop code to stopCode column in eventforbusstop model
"""
def fillStopCodeColumnInEventforbusstop(apps, schema_editor):
    ''' '''
    stopM = apps.get_model('AndroidRequests', 'busstop')
    eventforbusstopM = apps.get_model('AndroidRequests', 'eventforbusstop')
    for stop in stopM.objects.all():
        eventforbusstopM.objects.filter(busStop=stop).update(stopCode=stop.code)
    print "Fill stop code column in eventforbusstop model -> completed"

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0025_auto_20170324_1429'),
    ]

    operations = [
        # eventforbusstop model
        migrations.AddField(
            model_name='eventforbusstop',
            name='stopCode',
            field=models.CharField(default="", max_length=6, db_index=True, verbose_name='Stop Code'),
            preserve_default=False,
        ),
        migrations.RunPython(fillStopCodeColumnInEventforbusstop),
    ]
