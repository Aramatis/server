# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0029_score_20170330_1443'),
    ]

    operations = [
        migrations.RenameField(
            model_name='busstop',
            old_name='latitud',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='busstop',
            old_name='longitud',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='devicepositionintime',
            old_name='latitud',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='devicepositionintime',
            old_name='longitud',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='poseintrajectoryoftoken',
            old_name='latitud',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='poseintrajectoryoftoken',
            old_name='longitud',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='latitud',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='longitud',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='servicelocation',
            old_name='latitud',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='servicelocation',
            old_name='longitud',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbus',
            old_name='latitud',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbus',
            old_name='longitud',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbusstop',
            old_name='latitud',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='stadisticdatafromregistrationbusstop',
            old_name='longitud',
            new_name='longitude',
        ),
    ]
