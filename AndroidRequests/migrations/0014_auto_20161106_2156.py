# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0013_auto_20161102_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='service',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='busassignment',
            name='service',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='service',
            name='service',
            field=models.CharField(
                max_length=11,
                serialize=False,
                verbose_name=b'Service',
                primary_key=True),
        ),
        migrations.AlterField(
            model_name='servicelocation',
            name='service',
            field=models.CharField(
                max_length=11, verbose_name=b'Service Code'),
        ),
        migrations.AlterField(
            model_name='servicesbybusstop',
            name='code',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='servicestopdistance',
            name='service',
            field=models.CharField(
                max_length=11, verbose_name=b'Service Code'),
        ),
    ]
