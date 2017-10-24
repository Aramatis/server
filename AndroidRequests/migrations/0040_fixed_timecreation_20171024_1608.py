# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fixed_timecreation(apps, schema_editor):
    tokens = apps.get_model('AndroidRequests', 'token')
    # trajectories = apps.get_model('AndroidRequests', 'poseintrajectoryoftoken')

    for token in tokens.objects.prefetch_related('poseintrajectoryoftoken_set').all():
        timeCreation = \
        token.poseintrajectoryoftoken_set.all().order_by("-timeCreation").first().values_list("timeCreation",
                                                                                              flat=True)[0]
        token.timeCreation = timeCreation
        token.save()


class Migration(migrations.Migration):
    dependencies = [
        ('AndroidRequests', '0039_auto_20171004_1118'),
    ]

    operations = [
        migrations.RunPython(fixed_timecreation,
                             reverse_code=migrations.RunPython.noop),
    ]
