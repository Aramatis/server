# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0011_auto_20161026_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='imageName',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
