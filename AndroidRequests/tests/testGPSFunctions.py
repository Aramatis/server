from django.test import TestCase

import AndroidRequests.gpsFunctions as Gps


class TestGPSFunctions(TestCase):

    def setUp(self):
        self.error = 0.05

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
