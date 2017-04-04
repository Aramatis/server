# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0027_delete_foreign_key_eventbybusstop_20170403_1615'),
    ]

    operations = [
        migrations.RenameField(
            model_name='devicepositionintime',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.RenameField(
            model_name='eventforbusstop',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.RenameField(
            model_name='eventforbusv2',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.RenameField(
            model_name='nearbybuseslog',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.RenameField(
            model_name='report',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbus',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbusstop',
            old_name='userId',
            new_name='phoneId',
        ),
        migrations.RenameField(
            model_name='token',
            old_name='userId',
            new_name='phoneId',
        ),
    ]
