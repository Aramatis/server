# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fixed_timecreation(apps, schema_editor):
    Token = apps.get_model('AndroidRequests', 'token')
    PoseTrajectoryOfToken = apps.get_model('AndroidRequests', 'poseintrajectoryoftoken')
    ScoreHistory = apps.get_model('AndroidRequests', 'scorehistory')
    counter = 0

    for token in Token.objects.all().iterator():
        locationObj = PoseTrajectoryOfToken.objects.filter(token=token).order_by("timeStamp").first()
        scoreHistoryObj = ScoreHistory.objects.filter(meta__icontains=token.token).first()

        if locationObj is not None:
            token.timeCreation = locationObj.timeStamp
        if scoreHistoryObj is not None and token.tranSappUser_id is None:
            token.tranSappUser_id = scoreHistoryObj.tranSappUser_id
        token.save()

        counter += 1
        print("{0} - token {1} updated".format(counter, token.id))


class Migration(migrations.Migration):
    dependencies = [
        ('AndroidRequests', '0041_transappuser_timecreation'),
    ]

    operations = [
        migrations.RunPython(fixed_timecreation,
                             reverse_code=migrations.RunPython.noop),
    ]
