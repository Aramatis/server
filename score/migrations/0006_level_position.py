# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0005_auto_20170315_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='position',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
