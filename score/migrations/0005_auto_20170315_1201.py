# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0004_auto_20170315_1151'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transappuser',
            old_name='socialNetwork',
            new_name='accountType',
        ),
    ]
