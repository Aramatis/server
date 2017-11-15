# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fixed_timecreation(apps, schema_editor):
    Token = apps.get_model('AndroidRequests', 'token')
    PoseTrajectoryOfToken = apps.get_model('AndroidRequests', 'poseintrajectoryoftoken')
    """
    counter = 0
    for token in Token.objects.filter().all():
        locationObj = \
        PoseTrajectoryOfToken.objects.filter(token=token).order_by("timeStamp").first()
        if locationObj is not None:
            token.timeCreation = locationObj.timeStamp
            token.save()
        counter += 1
        print("{0} - token {1} updated".format(counter, token.id))
    #'update "AndroidRequests_token" SET "timeCreation" = (SELECT "timeStamp" FROM "AndroidRequests_poseintrajectoryoftoken" WHERE token_id="AndroidRequests_token".id ORDER BY "timeStamp" LIMIT 1);'
    """

class Migration(migrations.Migration):
    dependencies = [
        ('AndroidRequests', '0039_auto_20171004_1118'),
    ]

    operations = [
        migrations.RunPython(fixed_timecreation,
                             reverse_code=migrations.RunPython.noop),
    ]
