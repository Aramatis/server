# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0024_auto_20170310_1450'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bus',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='bus',
            name='events',
        ),
        migrations.RemoveField(
            model_name='eventforbus',
            name='bus',
        ),
        migrations.RemoveField(
            model_name='eventforbus',
            name='event',
        ),
        migrations.DeleteModel(
            name='Bus',
        ),
        migrations.DeleteModel(
            name='EventForBus',
        ),
    ]
