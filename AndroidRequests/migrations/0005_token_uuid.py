# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0004_auto_20160927_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]
