from django.test import TestCase

# my stuff
from AndroidRequests.models import ServiceLocation, BusStop, ServiceStopDistance, Bus, Service, ServicesByBusStop

# Create your tests here.


class BusDirectionTestCase(TestCase):
    """ test for bus direction """

    def setUp(self):
        """ this method will automatically call for every single test """

        # dummy  bus
        self.service = '507'
        self.serviceCode = '507R'
        self.registrationPlate = 'AA1111'
        self.bus = Bus.objects.create(
            registrationPlate=self.registrationPlate,
            service=self.service)
        # dummy bus stop
        self.busStopCode = 'PA459'
        self.busStopName = 'dummy bus stop'

        # add dummy service and its path
        service = Service.objects.get_or_create(
            service=self.service,
            origin='origin_test',
            destiny='destination_test')[0]

        # add dummy bus stop
        busStop = BusStop.objects.create(
            code=self.busStopCode,
            name=self.busStopName,
            longitud=-1,
            latitud=-1)

        ServicesByBusStop.objects.create(
            busStop=busStop, service=service, code=self.serviceCode)
        # ServiceStopDistance.objects.create(busStop = busStop, service = serviceCode, distance = 124529)

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
        # set bus stop
        busStop = BusStop.objects.get(code=self.busStopCode)
        busStop.longitud = 100
        busStop.latitud = 95
        busStop.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=busStop, service=self.serviceCode, distance=45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        #              *
        #
        #              *
        #              B
        # *   *  P  *  *
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=10,
            longitud=120,
            latitud=-80)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=20,
            longitud=120,
            latitud=-90)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=30,
            longitud=120,
            latitud=-100)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=40,
            longitud=110,
            latitud=-100)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=50,
            longitud=90,
            latitud=-100)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=60,
            longitud=80,
            latitud=-100)

        distance = 25

        # print "upper_right_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual(orientation, 'left')

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
        busStop = BusStop.objects.get(code=self.busStopCode)
        busStop.longitud = -70.662800
        busStop.latitud = -33.447467
        busStop.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=busStop, service=self.serviceCode, distance=45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *   *  P  *  *
        #              B
        #              *
        #
        #              *
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=10,
            longitud=-70.660452,
            latitud=-33.45992)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=20,
            longitud=-70.660452,
            latitud=-33.458282)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=30,
            longitud=-70.660452,
            latitud=-33.456859)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=40,
            longitud=-70.662244,
            latitud=-33.456859)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=50,
            longitud=-70.663617,
            latitud=-33.456859)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=60,
            longitud=-70.664776,
            latitud=-33.456859)

        distance = 20

        # print "lower_right_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual(orientation, 'left')

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
        busStop = BusStop.objects.get(code=self.busStopCode)
        busStop.longitud = -70.662800
        busStop.latitud = -33.457091
        busStop.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=busStop, service=self.serviceCode, distance=45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *   *  P  *  *
        # B
        # *
        #
        # *
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=10,
            longitud=-70.664744,
            latitud=-33.459839)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=20,
            longitud=-70.664744,
            latitud=-33.458282)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=30,
            longitud=-70.664744,
            latitud=-33.457091)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=40,
            longitud=-70.663617,
            latitud=-33.457091)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=50,
            longitud=-70.662244,
            latitud=-33.457091)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=60,
            longitud=-70.660871,
            latitud=-33.457091)

        distance = 20
        # print "lower_left_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual(orientation, 'right')

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
        busStop = BusStop.objects.get(code=self.busStopCode)
        busStop.longitud = 140
        busStop.latitud = -33.457199
        busStop.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=busStop, service=self.serviceCode, distance=45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *
        #
        # *
        # B
        # *   *  P  *  *
        #
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=10,
            longitud=120,
            latitud=-33.454325)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=20,
            longitud=120,
            latitud=-33.4554)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=30,
            longitud=120,
            latitud=-33.457199)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=40,
            longitud=130,
            latitud=-33.457199)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=50,
            longitud=150,
            latitud=-33.457199)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            distance=60,
            longitud=160,
            latitud=-33.457199)

        distance = 25

        # print "upper_left_corner"
        orientation = self.bus.getDirection(self.busStopCode, distance)

        self.assertEqual(orientation, 'right')
