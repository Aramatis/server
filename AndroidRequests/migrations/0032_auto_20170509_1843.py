# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0031_auto_20170424_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='stadisticdatafromregistrationbusstop',
            name='tranSappUser',
            field=models.ForeignKey(to='AndroidRequests.TranSappUser', null=True),
        ),
        migrations.AddField(
            model_name='stadisticdatafromregistrationbus',
            name='tranSappUser',
            field=models.ForeignKey(to='AndroidRequests.TranSappUser', null=True),
        ),
        migrations.AddField(
            model_name='transappuser',
            name='busAvatarId',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='transappuser',
            name='nickname',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transappuser',
            name='photoURI',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transappuser',
            name='showAvatar',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='transappuser',
            name='userAvatarId',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='eventforbusstop',
            name='expireTime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='eventforbusv2',
            name='expireTime',field=models.DateTimeField(null=True),
        ),
    ]
