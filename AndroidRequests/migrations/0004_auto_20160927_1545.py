# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0003_auto_20160927_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
