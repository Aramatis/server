from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.utils import timezone

from AndroidRequests.allviews.ServiceRoute import ServiceRoute
from gtfs.models import Route, GTFS

import json


class ServiceRouteTestCase(TestCase):
    """ test for ServiceRoute view """

    def setUp(self):

        # create dummy service
        self.gtfs = GTFS.objects.create(version=settings.GTFS_VERSION, timeCreation=timezone.now())
        self.service = "506"
        self.serviceCodeI = "506I"
        self.serviceCodeR = "506R"

        # create a service route for a dummy service
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=1,
            latitude=1,
            longitude=1)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=2,
            latitude=2,
            longitude=2)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=3,
            latitude=3,
            longitude=3)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=4,
            latitude=4,
            longitude=4)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=5,
            latitude=5,
            longitude=5)

        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=6,
            latitude=6,
            longitude=6)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=7,
            latitude=7,
            longitude=7)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=8,
            latitude=8,
            longitude=8)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=9,
            latitude=9,
            longitude=9)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=10,
            latitude=10,
            longitude=10)

        self.factory = RequestFactory()

    def test_get_route_for_service(self):
        """ test service route for concrete service  """
        request = self.factory.get('/android/requestRouteForService/')
        request.user = AnonymousUser()

        reponse_view = ServiceRoute()
        lat1 = 1
        lon1 = 1
        lat2 = 2
        lon2 = 2
        response = reponse_view.get(
            request, self.service, lat1, lon1, lat2, lon2)

        json_response = json.loads(response.content)

        self.assertEqual(json_response['service'], self.service)
        self.assertEqual(json_response['statusMessage'], "ok")
        self.assertEqual(json_response['statusCode'], "200")

        index = 1

        for route in json_response['route']:
            if index < 6:
                self.assertEqual(route['variant'], self.serviceCodeI)
            else:
                self.assertEqual(route['variant'], self.serviceCodeR)

            for point in route['route']:
                self.assertEqual(point['sequence'], index)
                self.assertEqual(point['latitude'], index)
                self.assertEqual(point['longitude'], index)
                index += 1

    def test_getRouteForServiceWithoutRoute(self):
        """ get route for a service without route points """
        request = self.factory.get('/android/requestRouteForService/')
        request.user = AnonymousUser()

        reponse_view = ServiceRoute()
        lat1 = 1
        lon1 = 1
        lat2 = 2
        lon2 = 2
        response = reponse_view.get(request, '507', lat1, lon1, lat2, lon2)

        json_response = json.loads(response.content)

        self.assertEqual(json_response['service'], '507')
        self.assertEqual(
            json_response['statusMessage'],
            "Service does not have route in the database.")
        self.assertEqual(json_response['statusCode'], "300")
