# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0006_level_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='level',
            name='position',
            field=models.IntegerField(unique=True),
        ),
    ]
