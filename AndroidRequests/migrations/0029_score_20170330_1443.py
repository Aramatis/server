# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndroidRequests', '0028_auto_20170404_1335'),
    ]

    operations = [
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('minScore', models.FloatField(default=0)),
                ('maxScore', models.FloatField(default=0)),
                ('position', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScoreEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=10)),
                ('score', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ScoreHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeCreation', models.DateTimeField(null=False)),
                ('scoreEvent', models.ForeignKey(to='AndroidRequests.ScoreEvent')),
                ('meta', models.CharField(max_length=10000, null=True)),
                ('score', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TranSappUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('userId', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phoneId', models.UUIDField()),
                ('accountType', models.CharField(max_length=10, choices=[(b'FACEBOOK', b'Facebook'), (b'GOOGLE', b'Google')])),
                ('globalScore', models.FloatField(default=0)),
                ('sessionToken', models.UUIDField()),
                ('level', models.ForeignKey(to='AndroidRequests.Level')),
            ],
        ),
        migrations.AddField(
            model_name='scorehistory',
            name='tranSappUser',
            field=models.ForeignKey(to='AndroidRequests.TranSappUser'),
        ),
        migrations.AddField(
            model_name='token',
            name='userEvaluation',
            field=models.IntegerField(null=True),
        ),
    ]
