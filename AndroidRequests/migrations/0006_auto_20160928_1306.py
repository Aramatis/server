# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import migrations


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model('AndroidRequests', 'token')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0005_token_uuid'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
