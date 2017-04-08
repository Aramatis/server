# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanner', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.AddField(
            model_name='log',
            name='timeStamp',
            field=models.DateTimeField(null=True),
        ),
    ]
