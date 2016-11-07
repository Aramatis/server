from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json

# my stuff
from AndroidRequests.models import *
from AndroidRequests.tests.testHelper import TestHelper
# views
from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.SendPoses import SendPoses
import AndroidRequests.views as views
import AndroidRequests.constants as Constants

class EndRouteTest(TestCase):
    """ test for end route url """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.helper = TestHelper(self)

        self.service = '507'
        self.licencePlate = 'PABJ45'

        self.helper.insertServicesOnDatabase([self.service])

    def test_endRouteWithValidActiveToken(self):
        """ finish active travel """

        travelKey = self.helper.getInBusWithLicencePlate(self.userId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        jsonResponse = self.helper.endRoute(travelKey)

        self.assertEqual(jsonResponse['response'], 'Trip ended.')

    def test_endRouteWithInvalidActiveToken(self):
        """ finish unactive travel """

        travelKey = self.helper.getInBusWithLicencePlate(self.userId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        self.helper.endRoute(travelKey)

        jsonResponse = self.helper.endRoute(travelKey)

        self.assertEqual(jsonResponse['response'], 'Token doesn\'t exist.')
