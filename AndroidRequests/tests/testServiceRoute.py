from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.conf import settings

import json

# my stuff
from AndroidRequests.models import Route, GTFS
# views
from AndroidRequests.allviews.ServiceRoute import ServiceRoute


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
            latitud=1,
            longitud=1)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=2,
            latitud=2,
            longitud=2)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=3,
            latitud=3,
            longitud=3)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=4,
            latitud=4,
            longitud=4)
        Route.objects.create(
            serviceCode=self.serviceCodeI,
            gtfs=self.gtfs,
            sequence=5,
            latitud=5,
            longitud=5)

        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=6,
            latitud=6,
            longitud=6)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=7,
            latitud=7,
            longitud=7)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=8,
            latitud=8,
            longitud=8)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=9,
            latitud=9,
            longitud=9)
        Route.objects.create(
            serviceCode=self.serviceCodeR,
            gtfs=self.gtfs,
            sequence=10,
            latitud=10,
            longitud=10)

        self.factory = RequestFactory()

    def test_get_route_for_service(self):
        """ test service route for concrete service  """
        request = self.factory.get('/android/requestRouteForService/')
        request.user = AnonymousUser()

        reponseView = ServiceRoute()
        lat1 = 1
        lon1 = 1
        lat2 = 2
        lon2 = 2
        response = reponseView.get(
            request, self.service, lat1, lon1, lat2, lon2)

        jsonResponse = json.loads(response.content)

        self.assertEqual(jsonResponse['service'], self.service)
        self.assertEqual(jsonResponse['statusMessage'], "ok")
        self.assertEqual(jsonResponse['statusCode'], "200")

        index = 1

        for route in jsonResponse['route']:
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

        reponseView = ServiceRoute()
        lat1 = 1
        lon1 = 1
        lat2 = 2
        lon2 = 2
        response = reponseView.get(request, '507', lat1, lon1, lat2, lon2)

        jsonResponse = json.loads(response.content)

        self.assertEqual(jsonResponse['service'], '507')
        self.assertEqual(
            jsonResponse['statusMessage'],
            "Service does not have route in the database.")
        self.assertEqual(jsonResponse['statusCode'], "300")
