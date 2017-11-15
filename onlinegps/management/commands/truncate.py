# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from onlinegps.models import LastGPS

import time


class Command(BaseCommand):
    help = "executes truncate command for model given by params"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        start_time = time.time()
        table_name = LastGPS._meta.db_table
        try:
            with connection.cursor() as cursor:
                cursor.execute("TRUNCATE %s" % table_name)
            total_time = time.time() - start_time
            self.stdout.write(self.style.SUCCESS("truncate on table %s successful: %s seconds" % (table_name, total_time)))
        except Exception as e:
            raise CommandError(e.message)
