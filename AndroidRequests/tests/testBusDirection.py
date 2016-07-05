from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json

# my stuff
from AndroidRequests.models import *
# views
from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.SendPoses import SendPoses
import AndroidRequests.views as views

# Create your tests here.

class BusDirectionTestCase(TestCase):
    """ test for bus direction """
    def setUp(self):
        """ this method will automatically call for every single test """

        # dummy  bus
        self.service = '507'
        self.serviceCode = '507I'
        self.registrationPlate = 'AA1111'
        self.bus = Bus.objects.create(registrationPlate = self.registrationPlate, service = self.service)
        # dummy bus stop
        self.busStopCode = 'PA459'
        self.busStopName = 'dummy bus stop'

        # add dummy service and its path
        Service.objects.create(service = self.service, origin = 'origin_test', destiny = 'destination_test')

    def test_bus_in_the_upper_right_corner_to_bus_stop(self):
        """
        Bus in the upper right corner, so the bus have to see to the left
        --------------------------
        |                        |
        |                        |
        |                  Bus   |
        |                        |
        |                        |
        |           -'-          |
        |            '           |
        |                        |
        |                        |
        |                        |
        |                        |
        --------------------------
        """
        # create bus stop
        busStop = BusStop.objects.create(code=self.busStopCode, name=self.busStopName, longitud=100, latitud=100)

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(busStop = busStop,  service = self.serviceCode, distance = 45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        #              *
        #
        #              *
        #              B
        # *   *  P  *  *
        ServiceLocation.objects.create(service = self.serviceCode, distance = 10, longitud=120, latitud=80)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 20, longitud=120, latitud=90)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 30, longitud=120, latitud=100)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 40, longitud=110, latitud=100)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 50, longitud=90, latitud=100)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 60, longitud=80, latitud=100)

        distance = 25

        print "upper_right_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual( orientation, 'left')

    def test_bus_in_the_lower_right_corner_to_bus_stop(self):
        """
        Bus in the lower right corner, so the bus have to see to the left
        --------------------------
        |                        |
        |                        |
        |                        |
        |                        |
        |                        |
        |           -'-          |
        |            '           |
        |                        |
        |                        |
        |                  Bus   |
        |                        |
        --------------------------
        """
        # create bus stop
        busStop = BusStop.objects.create(code=self.busStopCode, name=self.busStopName, longitud=-70.662800, latitud=-33.447467)

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(busStop = busStop,  service = self.serviceCode, distance = 45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *   *  P  *  *
        #              B
        #              *
        #
        #              *
        ServiceLocation.objects.create(service = self.serviceCode, distance = 10, longitud=-70.660452, latitud=-33.45992)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 20, longitud=-70.660452, latitud=-33.458282)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 30, longitud=-70.660452, latitud=-33.456859)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 40, longitud=-70.662244, latitud=-33.456859)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 50, longitud=-70.663617, latitud=-33.456859)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 60, longitud=-70.664776, latitud=-33.456859)

        distance = 20

        print "lower_right_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual( orientation, 'left')

    def test_bus_in_the_lower_left_corner_to_bus_stop(self):
        """
        Bus in the lower left corner, so the bus have to see to the left
        --------------------------
        |                        |
        |                        |
        |                        |
        |                        |
        |                        |
        |           -'-          |
        |            '           |
        |                        |
        |                        |
        |    Bus                 |
        |                        |
        --------------------------
        """
        # create bus stop
        busStop = BusStop.objects.create(code=self.busStopCode, name=self.busStopName, longitud=-70.662800, latitud=-33.457091)

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(busStop = busStop,  service = self.serviceCode, distance = 45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *   *  P  *  *
        # B
        # *
        #
        # *
        ServiceLocation.objects.create(service = self.serviceCode, distance = 10, longitud=-70.664744, latitud=-33.459839)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 20, longitud=-70.664744, latitud=-33.458282)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 30, longitud=-70.664744, latitud=-33.457091)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 40, longitud=-70.663617, latitud=-33.457091)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 50, longitud=-70.662244, latitud=-33.457091)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 60, longitud=-70.660871, latitud=-33.457091)

        distance = 20
        print "lower_left_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual( orientation, 'right')

    def test_bus_in_the_upper_left_corner_to_bus_stop(self):
        """
        Bus in the upper left corner, so the bus have to see to the left
        --------------------------
        |                        |
        |    Bus                 |
        |                        |
        |                        |
        |                        |
        |           -'-          |
        |            '           |
        |                        |
        |                        |
        |                        |
        |                        |
        --------------------------
        """
        # create bus stop
        busStop = BusStop.objects.create(code=self.busStopCode, name=self.busStopName, longitud=-70.662800, latitud=-33.457199)

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(busStop = busStop,  service = self.serviceCode, distance = 45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *
        #
        # *
        # B
        # *   *  P  *  *
        #
        ServiceLocation.objects.create(service = self.serviceCode, distance = 10, longitud=-70.664819, latitud=-33.454325)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 20, longitud=-70.664819, latitud=-33.4554)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 30, longitud=-70.664819, latitud=-33.457199)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 40, longitud=-70.663617, latitud=-33.457199)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 50, longitud=-70.662244, latitud=-33.457199)
        ServiceLocation.objects.create(service = self.serviceCode, distance = 60, longitud=-70.660871, latitud=-33.457199)

        distance = 20

        print "upper_left_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual( orientation, 'right')


