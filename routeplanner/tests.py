# encoding=utf-8
from django.test import TestCase, RequestFactory, Client
from routeplanner.views import RoutePlanner

import routeplanner.views as views
import urllib
import json

class RoutePlannerTest(TestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """
        self.factory = RequestFactory()
        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

    def test_getCitySuffix(self):
        """   """

        origin = "-33.456769,-70.652883"
        destination = "beauchef 850"

        view = RoutePlanner()

        newOrigin = view.addCitySuffix(origin)
        newDestination = view.addCitySuffix(destination)

        self.assertEqual(origin, newOrigin)
        self.assertEqual(destination + " " + views.CITY_SUFFIX, newDestination)

    def test_getCitySuffixWithAccentWord(self):
        """   """

        origin = "-33.456769,-70.652883"
        destination = "Universidad del pacífico"

        view = RoutePlanner()

        newOrigin = view.addCitySuffix(origin)
        newDestination = view.addCitySuffix(destination)

        self.assertEqual(origin, newOrigin)
        self.assertEqual(destination + " " + views.CITY_SUFFIX, newDestination)

    def calculateTrip(self, phoneId, origin, destination):
        URL = '/routeplanner/calculate/'
        URL = URL + '/'.join([phoneId, origin, destination])
        URL = urllib.quote(URL)
        c = Client()
        data = {}
        #    'phoneId': self.phoneId,
        #    'origin': origin,
        #    'destination': destination}
        response = c.get(URL, data)
        self.assertEqual(response.status_code, 200)
        #jsonResponse = json.loads(response.content)
        #print jsonResponse

    def test_calculateTripWithGoodParams(self):
        origin = 'beauchef 850'
        destination = 'santo domingo 1325'

        self.calculateTrip(self.phoneId, origin, destination)

    def test_calculateTripWithNullPhoneId(self):
        phoneId = 'null'
        origin = 'beauchef 850'
        destination = 'santo domingo 1325'

        self.calculateTrip(phoneId, origin, destination)
