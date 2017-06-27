# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0006_auto_20160928_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='uuid',
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False),
        ),
    ]
