# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phoneId', models.UUIDField()),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('minScore', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ScoreEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('score', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ScoreHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeCreation', models.DateTimeField()),
                ('score', models.FloatField(default=0)),
                ('meta', models.CharField(max_length=100, null=True)),
                ('scoreEvent', models.ForeignKey(to='score.ScoreEvent')),
            ],
        ),
        migrations.CreateModel(
            name='TranSappUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tokenId', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('socialNetwork', models.CharField(max_length=10, choices=[(b'FACEBOOK', b'Facebook'), (b'GOOGLE', b'Google')])),
                ('globalScore', models.FloatField(default=0)),
                ('level', models.ForeignKey(to='score.Level')),
            ],
        ),
        migrations.AddField(
            model_name='scorehistory',
            name='tranSappUser',
            field=models.ForeignKey(to='score.TranSappUser'),
        ),
        migrations.AddField(
            model_name='activeuser',
            name='tranSappUser',
            field=models.ForeignKey(to='score.TranSappUser'),
        ),
    ]
