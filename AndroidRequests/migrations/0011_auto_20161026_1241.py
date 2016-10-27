# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0010_auto_20161013_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='imageName',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
