# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-02 15:40
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


def create_uuid(apps, schema_editor):
    User = apps.get_model('AndroidRequests', 'TranSappUser')
    for track in User.objects.all():
        track.externalId = uuid.uuid4()
        track.save()


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0035_auto_20170914_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='transappuser',
            name='externalId',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(create_uuid)
    ]