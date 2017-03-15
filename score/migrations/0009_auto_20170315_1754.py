# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0008_transappuser_phoneid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transappuser',
            name='level',
            field=models.ForeignKey(to='score.Level'),
        ),
        migrations.AlterField(
            model_name='transappuser',
            name='sessionToken',
            field=models.UUIDField(),
        ),
    ]
