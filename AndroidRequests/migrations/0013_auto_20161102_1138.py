# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.exceptions import ObjectDoesNotExist


def fill_table(apps, schema_editor):
    busesassignments = apps.get_model('AndroidRequests', 'busassignment')
    tokens = apps.get_model('AndroidRequests', 'token')
    eventsForBusv2 = apps.get_model('AndroidRequests', 'EventForBusv2')
    for assignment in busesassignments.objects.all():
        if assignment.service.isupper():
            try:
                correct = busesassignments.objects.get(uuid=assignment.uuid,
                                                       service=assignment.service.lower())
                for token in tokens.objects.filter(busassignment=assignment):
                    token.busassignment = correct
                    token.save()
                for event in eventsForBusv2.objects.filter(
                        busassignment=assignment):
                    event.busassignment = correct
                    event.save()
                assignment.delete()
            except ObjectDoesNotExist:
                assignment.service = assignment.service.lower()
                assignment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0012_auto_20161026_1243'),
    ]

    operations = [
        migrations.RunPython(fill_table,
                             reverse_code=migrations.RunPython.noop),
    ]
