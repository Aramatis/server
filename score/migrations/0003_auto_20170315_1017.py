# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0002_auto_20170314_1436'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transappuser',
            old_name='tokenId',
            new_name='userId',
        ),
        migrations.AlterField(
            model_name='transappuser',
            name='level',
            field=models.ForeignKey(default=1, to='score.Level'),
        ),
    ]
