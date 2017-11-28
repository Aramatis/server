from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.utils import timezone

from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.models import Service, BusStop, ServicesByBusStop
from gtfs.models import GTFS

import json


class BusStopsByServiceTestCase(TestCase):
    """ test for BusStopByService view """

    def setUp(self):
        
        gtfs_obj = GTFS.objects.create(version=settings.GTFS_VERSION, timeCreation=timezone.now())
        # create dummy service
        self.service = "506"
        route_code = "506I"
        route_obj = Service.objects.create(
            service=self.service,
            gtfs=gtfs_obj,
            origin="this is the origin location",
            destiny="this es the destiny location")

        # create set of bus stop for dummy service
        self.bus_stop_objs = []

        codes = ["PA60", "PA61", "PA62"]
        names = [
            "bus top name for PA60",
            "bus top name for PA61",
            "bus top name for PA62"]
        latitudes = [-33.4577491104941, -33.4445256604888, -33.4402777996082]
        longitudes = [-70.6634020999999, -70.6509264499999, -70.6433333]

        for index in [0, 1, 2]:
            self.bus_stop_objs.append(BusStop.objects.create(
                code=codes[index],
                gtfs=gtfs_obj,
                name=names[index],
                latitude=latitudes[index],
                longitude=longitudes[index]
            ))

        # associate bus stop with service
        for index in [0, 1, 2]:
            ServicesByBusStop.objects.create(
                code=route_code,
                busStop=self.bus_stop_objs[index],
                gtfs=gtfs_obj,
                service=route_obj
            )

        self.factory = RequestFactory()

    def test_get_busstop_for_service(self):
        """ test bus stops for concrete service  """
        request = self.factory.get('/android/requestBusStopsByService/')
        request.user = AnonymousUser()

        reponse_view = BusStopsByService()
        response = reponse_view.get(request, self.service)

        json_response = json.loads(response.content)

        self.assertEqual(json_response['service'], self.service)
        index = 0
        for busStop in json_response['paraderos']:
            self.assertEqual(
                busStop['latitud'],
                self.bus_stop_objs[index].latitud)
            self.assertEqual(
                busStop['longitud'],
                self.bus_stop_objs[index].longitud)
            self.assertEqual(busStop['nombre'], self.bus_stop_objs[index].name)
            self.assertEqual(busStop['codigo'], self.bus_stop_objs[index].code)
            index += 1
