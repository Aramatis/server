# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activeuser',
            name='tranSappUser',
        ),
        migrations.AddField(
            model_name='transappuser',
            name='sessionId',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.DeleteModel(
            name='ActiveUser',
        ),
    ]
