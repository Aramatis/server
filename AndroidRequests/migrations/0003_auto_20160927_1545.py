# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import AndroidRequests.constants as Constants

def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model('AndroidRequests', 'bus')
    uuidsArray = {}
    for row in MyModel.objects.all():
        if row.registrationPlate == Constants.DUMMY_LICENSE_PLATE:
            puuid = uuid.uuid4()
            row.uuid = puuid
        elif row.registrationPlate in uuidsArray:
            row.uuid = uuidsArray[row.registrationPlate]
        else:
            puuid = uuid.uuid4()
            row.uuid = puuid
            uuidsArray[row.registrationPlate] = puuid
        row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0002_bus_uuid'),
    ]

    operations = [
    	migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
