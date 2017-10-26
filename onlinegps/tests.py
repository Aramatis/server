# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command
from io import BytesIO


class CommandsTest(TestCase):

    def test_command_truncate_output(self):
        """ test command truncate """
        out = BytesIO()
        call_command('truncate', stdout=out)
        self.assertIn("truncate on table ", out.getvalue())

    def test_command_loadgpspoints_output(self):
        """ test command loadgpspoints """
        out = BytesIO()
        test_file_name = "test_ultimos_gps.csv.gz"
        call_command("loadgpspoints", test_file_name, stdout=out)
        self.assertIn("copy on table ", out.getvalue())
