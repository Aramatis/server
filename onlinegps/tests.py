# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command
from io import BytesIO

from onlinegps.views import get_locations, get_user_route, get_direction
from onlinegps.models import LastGPS


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


class VehicleDataTest(TestCase):
    """ test functions to get data related with license plate """

    def test_get_locations(self):
        """ test get_location function """
        test_file_name = "test_ultimos_gps.csv.gz"
        call_command("loadgpspoints", test_file_name)

        license_plates = LastGPS.objects.values_list("licensePlate", flat=True)

        answer = get_locations(license_plates)

        for key, value in answer.iteritems():
            self.assertIsNotNone(value["latitude"])
            self.assertIsNotNone(value["longitude"])
            if value["direction"] is None or value["route"] is None:
                pass

    def test_get_direction(self):
        """ test get_direction function """
        routes = ["B01I", "102R", "506eI", "506NI", "B03I_fjudo", "B04vI", "C02cR"]
        expected_answer = ["I", "R", "I", "I", "I", "I", "R"]

        for index, route in enumerate(routes):
            self.assertEquals(get_direction(route), expected_answer[index])

    def test_get_user_route(self):
        """ test get_user_route function """
        routes = ["B01I", "102R", "506eI", "506NI", "B03I_fjudo", "B04vI", "C02cR"]
        expected_answer = ["B01", "102", "506e", "506N", "B03", "B04v", "C02c"]

        for index, route in enumerate(routes):
            self.assertEquals(get_user_route(route), expected_answer[index])