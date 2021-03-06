from django.conf import settings
from django.test import TestCase

from AndroidRequests.models import ServiceLocation, BusStop, ServiceStopDistance, Busassignment, GTFS
from AndroidRequests.tests.testHelper import TestHelper


class BusDirectionTestCase(TestCase):
    """ test for bus direction """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.test = TestHelper(self)

        # dummy data
        self.service = '507'
        self.serviceCode = '507R'
        self.registrationPlate = 'AA1111'

        # add service
        self.test.insertServicesOnDatabase([self.service])

        # add bus stop
        self.stopCode = 'PA459'
        self.test.insertBusstopsOnDatabase([self.stopCode])
        self.stopObj = BusStop.objects.get(code=self.stopCode)

        self.test.insertServicesByBusstopsOnDatabase([self.stopCode])

        # create bus
        phoneId = 'dec51b413a954765abb415524c04c807'
        self.test.createBusAndAssignmentOnDatabase(phoneId, self.service, self.registrationPlate)

        self.gtfs = GTFS.objects.get(version=settings.GTFS_VERSION)

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
        self.stopObj.longitude = 100
        self.stopObj.latitude = 95
        self.stopObj.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stopObj, gtfs=self.gtfs, service=self.serviceCode, distance=45)
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
            gtfs=self.gtfs,
            distance=10,
            longitude=120,
            latitude=-80)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=20,
            longitude=120,
            latitude=-90)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=30,
            longitude=120,
            latitude=-100)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=40,
            longitude=110,
            latitude=-100)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=50,
            longitude=90,
            latitude=-100)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=60,
            longitude=80,
            latitude=-100)

        distance = 25

        # print "upper_right_corner"
        orientation = Busassignment.objects.first().getDirection(self.stopObj, distance)

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
        self.stopObj.longitude = -70.662800
        self.stopObj.latitude = -33.447467
        self.stopObj.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stopObj, gtfs=self.gtfs, service=self.serviceCode, distance=45)
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
            gtfs=self.gtfs,
            distance=10,
            longitude=-70.660452,
            latitude=-33.45992)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=20,
            longitude=-70.660452,
            latitude=-33.458282)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=30,
            longitude=-70.660452,
            latitude=-33.456859)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=40,
            longitude=-70.662244,
            latitude=-33.456859)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=50,
            longitude=-70.663617,
            latitude=-33.456859)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=60,
            longitude=-70.664776,
            latitude=-33.456859)

        distance = 20

        # print "lower_right_corner"
        orientation = Busassignment.objects.first().getDirection(self.stopObj, distance)

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
        self.stopObj.longitude = -70.662800
        self.stopObj.latitude = -33.457091
        self.stopObj.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stopObj, gtfs=self.gtfs, service=self.serviceCode, distance=45)
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
            gtfs=self.gtfs,
            distance=10,
            longitude=-70.664744,
            latitude=-33.459839)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=20,
            longitude=-70.664744,
            latitude=-33.458282)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=30,
            longitude=-70.664744,
            latitude=-33.457091)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=40,
            longitude=-70.663617,
            latitude=-33.457091)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=50,
            longitude=-70.662244,
            latitude=-33.457091)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=60,
            longitude=-70.660871,
            latitude=-33.457091)

        distance = 20
        # print "lower_left_corner"
        orientation = Busassignment.objects.first().getDirection(self.stopObj, distance)

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
        self.stopObj.longitude = 140
        self.stopObj.latitude = -33.457199
        self.stopObj.save()

        # self.serviceCode stops in  self.busStop
        ServiceStopDistance.objects.create(
            busStop=self.stopObj, gtfs=self.gtfs, service=self.serviceCode, distance=45)
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
            gtfs=self.gtfs,
            distance=10,
            longitude=120,
            latitude=-33.454325)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=20,
            longitude=120,
            latitude=-33.4554)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=30,
            longitude=120,
            latitude=-33.457199)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=40,
            longitude=130,
            latitude=-33.457199)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=50,
            longitude=150,
            latitude=-33.457199)
        ServiceLocation.objects.create(
            service=self.serviceCode,
            gtfs=self.gtfs,
            distance=60,
            longitude=160,
            latitude=-33.457199)

        distance = 25

        # print "upper_left_corner"
        orientation = Busassignment.objects.first().getDirection(self.stopObj, distance)

        self.assertEqual(orientation, 'right')
