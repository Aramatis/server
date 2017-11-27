from django.conf import settings
from django.test import TestCase

from AndroidRequests.models import ServiceLocation, BusStop, ServiceStopDistance, Busassignment
from gtfs.models import GTFS
from AndroidRequests.tests.testHelper import TestHelper


class BusDirectionTestCase(TestCase):
    """ test for bus direction """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.test = TestHelper(self)

        # dummy data
        self.route = '507'
        self.route_code = '507R'
        self.license_plate = 'AA1111'

        # add service
        self.test.insertServicesOnDatabase([self.route])

        # add bus stop
        self.stop_code = 'PA459'
        self.test.insertBusstopsOnDatabase([self.stop_code])
        self.stop_obj = BusStop.objects.get(code=self.stop_code)

        self.test.insertServicesByBusstopsOnDatabase([self.stop_code])

        # create bus
        phone_id = 'dec51b413a954765abb415524c04c807'
        self.test.createBusAndAssignmentOnDatabase(phone_id, self.route, self.license_plate)

        self.gtfs_obj = GTFS.objects.get(version=settings.GTFS_VERSION)

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
        self.stop_obj.longitude = 100
        self.stop_obj.latitude = 95
        self.stop_obj.save()

        # self.route_code stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stop_obj, gtfs=self.gtfs_obj, service=self.route_code, distance=45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        #              *
        #
        #              *
        #              B
        # *   *  P  *  *
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=10,
            longitude=120,
            latitude=-80)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=20,
            longitude=120,
            latitude=-90)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=30,
            longitude=120,
            latitude=-100)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=40,
            longitude=110,
            latitude=-100)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=50,
            longitude=90,
            latitude=-100)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=60,
            longitude=80,
            latitude=-100)

        distance = 25

        # print "upper_right_corner"
        orientation = Busassignment.objects.first().get_direction(self.stop_obj, distance)

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
        self.stop_obj.longitude = -70.662800
        self.stop_obj.latitude = -33.447467
        self.stop_obj.save()

        # self.route_code stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stop_obj, gtfs=self.gtfs_obj, service=self.route_code, distance=45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *   *  P  *  *
        #              B
        #              *
        #
        #              *
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=10,
            longitude=-70.660452,
            latitude=-33.45992)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=20,
            longitude=-70.660452,
            latitude=-33.458282)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=30,
            longitude=-70.660452,
            latitude=-33.456859)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=40,
            longitude=-70.662244,
            latitude=-33.456859)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=50,
            longitude=-70.663617,
            latitude=-33.456859)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=60,
            longitude=-70.664776,
            latitude=-33.456859)

        distance = 20

        # print "lower_right_corner"
        orientation = Busassignment.objects.first().get_direction(self.stop_obj, distance)

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
        self.stop_obj.longitude = -70.662800
        self.stop_obj.latitude = -33.457091
        self.stop_obj.save()

        # self.route_code stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stop_obj, gtfs=self.gtfs_obj, service=self.route_code, distance=45)
        # to select points uses itouchmap.com/latlong.html
        # this points generate this position scheme
        #
        # *   *  P  *  *
        # B
        # *
        #
        # *
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=10,
            longitude=-70.664744,
            latitude=-33.459839)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=20,
            longitude=-70.664744,
            latitude=-33.458282)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=30,
            longitude=-70.664744,
            latitude=-33.457091)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=40,
            longitude=-70.663617,
            latitude=-33.457091)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=50,
            longitude=-70.662244,
            latitude=-33.457091)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=60,
            longitude=-70.660871,
            latitude=-33.457091)

        distance = 20
        # print "lower_left_corner"
        orientation = Busassignment.objects.first().get_direction(self.stop_obj, distance)

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
        self.stop_obj.longitude = 140
        self.stop_obj.latitude = -33.457199
        self.stop_obj.save()

        # self.route_code stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stop_obj, gtfs=self.gtfs_obj, service=self.route_code, distance=45)
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
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=10,
            longitude=120,
            latitude=-33.454325)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=20,
            longitude=120,
            latitude=-33.4554)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=30,
            longitude=120,
            latitude=-33.457199)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=40,
            longitude=130,
            latitude=-33.457199)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=50,
            longitude=150,
            latitude=-33.457199)
        ServiceLocation.objects.create(
            service=self.route_code,
            gtfs=self.gtfs_obj,
            distance=60,
            longitude=160,
            latitude=-33.457199)

        distance = 25

        # print "upper_left_corner"
        orientation = Busassignment.objects.first().get_direction(self.stop_obj, distance)

        self.assertEqual(orientation, 'right')
