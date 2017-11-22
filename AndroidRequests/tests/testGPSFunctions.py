from django.test import TestCase
from django.utils.dateparse import parse_datetime

from datetime import datetime

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.constants as Constants
import AndroidRequests.gpsFunctions as Gps
import json


class TestGPSFunctions(TestCase):
    def setUp(self):
        # self.phoneId = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        # self.route = '506'
        # self.registrationPlate = 'XXYY25'
        self.error = 0.05
        self.jsonData = json.dumps({
            "machine": {
                "route": "T343 07R",
                "licencePlate": "FLXC49"
            },
            "diffTime": "0:04:44",
            "nearestGpsPoint": {
                "latitude": -33.46517531,
                "longitude": -70.63099175,
                "time": "2016-11-29T12:41:36"
            },
            "error": False
        }, cls=TranSappJSONEncoder)
        self.helper = TestHelper(self)

    def test_haversineFunction(self):
        lon1, lat1, lon2, lat2 = [-77.037852, 38.898556, -77.043934, 38.897147]
        result1 = Gps.haversine(lon1, lat1, lon2, lat2)
        expected1 = 549

        lon3, lat3, lon4, lat4 = [-77.037852, 38.898556, -77.037852, 38.898556]
        result2 = Gps.haversine(lon3, lat3, lon4, lat4)
        expected2 = 0

        self.assertGreaterEqual(result1, expected1 - expected1 * self.error)
        self.assertLessEqual(result1, expected1 + expected1 * self.error)
        self.assertGreaterEqual(result2, expected2 - expected2 * self.error)
        self.assertLessEqual(result2, expected2 + expected2 * self.error)

    def test_getGPSData(self):
        self.timeStamp = datetime.strptime(
            "2016-11-29 12:46:20", "%Y-%m-%d %H:%M:%S")
        plon = -70.63098
        plat = -33.46516
        jsonContent = self.jsonData
        longitud, latitud, time, distance = Gps.getGPSData(
            "FLXC49", self.timeStamp, plon, plat, jsonContent)
        data = json.loads(self.jsonData)
        expectedDistance = 2.021

        self.assertEqual(longitud, data['nearestGpsPoint']['longitude'])
        self.assertEqual(latitud, data['nearestGpsPoint']['latitude'])
        self.assertEqual(
            time,
            parse_datetime(
                data['nearestGpsPoint']['time'] +
                Constants.TIMEZONE))
        self.assertGreaterEqual(
            distance,
            expectedDistance -
            expectedDistance *
            self.error)
        self.assertLessEqual(
            distance,
            expectedDistance +
            expectedDistance *
            self.error)
