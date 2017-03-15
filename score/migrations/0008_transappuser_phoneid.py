# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('score', '0007_auto_20170315_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='transappuser',
            name='phoneId',
            field=models.UUIDField(default=uuid.uuid4),
            preserve_default=False,
        ),
    ]
