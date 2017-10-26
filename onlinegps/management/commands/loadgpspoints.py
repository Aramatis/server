# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings

from onlinegps.models import LastGPS

import time
import os
import gzip


class Command(BaseCommand):
    help = "load gps points from file (inside media folder of onlinegps app) to LastGPS model"

    def add_arguments(self, parser):
        parser.add_argument("file_name", help="file name with gps points")

    def handle(self, *args, **options):
        file_name = options["file_name"]
        start_time = time.time()
        table_name = "\"%s\"" % LastGPS._meta.db_table
        try:
            file_path = os.path.join(settings.BASE_DIR, "onlinegps", "media", file_name)
            with gzip.open(file_path, "r") as gps_file, connection.cursor() as cursor:
                cursor.execute("TRUNCATE %s" % table_name)
                cursor.copy_from(gps_file, table_name, ";")
            total_time = time.time() - start_time
            self.stdout.write(self.style.SUCCESS("copy on table %s successful: %s seconds" % (table_name, total_time)))
        except Exception as e:
            raise CommandError(str(e))
