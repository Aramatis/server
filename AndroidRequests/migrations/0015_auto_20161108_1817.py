# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0014_auto_20161106_2156'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='busassignment',
            unique_together=set([('uuid', 'service')]),
        ),
    ]
