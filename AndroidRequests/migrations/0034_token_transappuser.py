# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0033_auto_20170515_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='tranSappUser',
            field=models.ForeignKey(to='AndroidRequests.TranSappUser', null=True),
        ),
    ]
