# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fill_tables(apps, schema_editor):
    statisticsfrombus = apps.get_model(
        'AndroidRequests',
        'StadisticDataFromRegistrationBus')

    for sts in statisticsfrombus.objects.all():
        aux = sts.latitud
        sts.latitud = sts.longitud
        sts.longitud = aux
        sts.save()


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0015_auto_20161108_1817'),
    ]

    operations = [
        migrations.RunPython(fill_tables,
                             reverse_code=migrations.RunPython.noop),
    ]
