# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone

from io import BytesIO

from onlinegps.views import get_machine_locations, get_user_route, get_direction, is_near_to_bus_position, \
    get_real_machine_info_with_distance
from onlinegps.models import LastGPS

from AndroidRequests.gpsFunctions import haversine


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

    def setUp(self):
        self.test_file_name = "test_ultimos_gps.csv.gz"

    def test_get_locations(self):
        """ test get_location function """
        call_command("loadgpspoints", self.test_file_name)

        license_plates = list(LastGPS.objects.values_list("licensePlate", flat=True))

        answer = get_machine_locations(license_plates)

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

    def test_get_real_machine_info(self):
        # create record
        license_plate = "AFBG45"
        route = "506I"
        timestamp = timezone.now()
        latitude = -33.457136
        longitude = -70.664040
        LastGPS.objects.create(licensePlate=license_plate, userRouteCode=route, timestamp=timestamp,
                               longitude=longitude, latitude=latitude)

        answer = get_real_machine_info_with_distance(license_plate, longitude, latitude)

        self.assertEquals(answer[0], longitude)
        self.assertEquals(answer[1], latitude)
        self.assertEquals(answer[2], timestamp)
        self.assertEquals(answer[3], 0)


class UserBusIsNearToRealBusTest(TestCase):
    """ test functions to know if user bus is near to real bus (based on gps) """

    def setUp(self):
        self.test_file_name = "test_ultimos_gps.csv.gz"
        call_command("loadgpspoints", self.test_file_name)
        self.license_plate = "CJRB74"

    def test_give_empty_list(self):
        """ test is_near_to_bus_position function. It receives empty list"""
        positions = []
        self.assertRaises(AssertionError, is_near_to_bus_position, self.license_plate, positions)

    def get_tuple(self, time_deltas, locations=None):

        machine_info = get_machine_locations([self.license_plate])[self.license_plate]

        now = machine_info["timestamp"]
        times = []
        for time_delta in time_deltas:
            times.append(now - timezone.timedelta(seconds=time_delta))

        if locations == None:
            locations = [
                (-70.647482, -33.380137),  # nearest point
                (-70.64712, -33.380238),
                (-70.646807, -33.380336),
                (-70.64645, -33.380492)
            ]

        distance = haversine(machine_info["longitude"], machine_info["latitude"], locations[0][0], locations[0][1])
        print("distance:", distance, " diffTime:", abs((now - times[0]).total_seconds()))

        positions = [(lon, lat, tz) for (lon, lat), tz in zip(locations, times)]

        return positions

    def test_time_ok_but_distance_not_ok(self):
        """ time diff 1 second but distance less than 500 meter """

        time_deltas = [1, 2, 4, 6]

        positions = self.get_tuple(time_deltas)
        self.assertTrue(is_near_to_bus_position(self.license_plate, positions))

        time_deltas = [-1, -2, -4, -6]
        positions = self.get_tuple(time_deltas)
        self.assertTrue(is_near_to_bus_position(self.license_plate, positions))

    def test_time_not_ok_and_distance_not_ok(self):
        """ time diff 30 seconds and distance less than 500 meter """

        time_deltas = [30, 32, 44, 56]

        positions = self.get_tuple(time_deltas)
        self.assertTrue(is_near_to_bus_position(self.license_plate, positions))

        time_deltas = [-30, -32, -44, -56]
        positions = self.get_tuple(time_deltas)
        self.assertTrue(is_near_to_bus_position(self.license_plate, positions))

    def test_time_not_ok_and_distance_ok(self):
        """ time diff 30 seconds but distance greater than 500 meter """

        time_deltas = [30, 32, 44, 56]
        locations = [
            (-70.662764, -33.374385),  # nearest point
            (-70.665184, -33.373490),
            (-70.667759, -33.372531),
            (-70.670559, -33.371447)
        ]

        positions = self.get_tuple(time_deltas, locations)
        self.assertTrue(is_near_to_bus_position(self.license_plate, positions))

        time_deltas = [-30, -32, -44, -56]
        positions = self.get_tuple(time_deltas, locations)
        self.assertTrue(is_near_to_bus_position(self.license_plate, positions))

    def test_time_ok_and_distance_ok(self):
        """ time diff 10 seconds but distance greater than 500 meter """

        # negative indicate that user points are newer than bus gps
        time_deltas = [-9, -11, -24, -36]
        locations = [
            (-70.662764, -33.374385),  # nearest point
            (-70.665184, -33.373490),
            (-70.667759, -33.372531),
            (-70.670559, -33.371447)
        ]

        positions = self.get_tuple(time_deltas, locations)
        self.assertFalse(is_near_to_bus_position(self.license_plate, positions))

        time_deltas = [9, 11, 24, 36]
        positions = self.get_tuple(time_deltas, locations)
        self.assertFalse(is_near_to_bus_position(self.license_plate, positions))

    def test_license_plate_does_not_exist(self):
        """ license plate does not exist in database """

        license_plate = "this_is_a_fake_license_plate"

        # negative indicate that user points are newer than bus gps
        time_deltas = [9, 11, 24, 36]

        positions = self.get_tuple(time_deltas)
        self.assertTrue(is_near_to_bus_position(license_plate, positions))
