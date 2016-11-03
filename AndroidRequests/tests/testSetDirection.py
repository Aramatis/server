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

class SetDirectionTest(TestCase):
    """ test for Setdirection url """

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.helper = TestHelper(self)

        self.service = '507'
        self.licencePlate = 'PABJ45'
        self.busStop = 'PA459'

        self.helper.insertServicesOnDatabase([self.service])
        self.helper.insertBusstopsOnDatabase([self.busStop])
        self.helper.insertServicesByBusstopsOnDatabase([self.busStop])

    def test_setDirectionWithActiveTokenWithDummyLicencePlate(self):
        """ set direction of travel has not been finished with dummy licence plate """

        travelKey = self.helper.getInBusWithLicencePlate(self.userId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], True)
            self.assertEqual(jsonResponse['message'], "User bus direction updated.")

        self.helper.endRoute(travelKey)

    def test_setDirectionWithActiveToken(self):
        """ set direction of travel has not been finished """

        travelKey = self.helper.getInBusWithLicencePlate(self.userId, self.service, self.licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], True)
            self.assertEqual(jsonResponse['message'], "User bus direction updated.")

        self.helper.endRoute(travelKey)

    def test_setDirectionWithoutActiveToken(self):
        """ set direction of travel has been finished """

        travelKey = self.helper.getInBusWithLicencePlate(self.userId, self.service, self.licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.endRoute(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], False)
            self.assertEqual(jsonResponse['message'], "Token doesn't exist.")

    def test_setDirectionWithoutActiveTokenWithDummyLicencePlate(self):
        """ set direction of travel has been finished """

        travelKey = self.helper.getInBusWithLicencePlate(self.userId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.endRoute(travelKey)

        directions = ["I", "R"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], False)
            self.assertEqual(jsonResponse['message'], "Token doesn't exist.")

    def test_setDirectionWithWrongDirection(self):
        """ set direction of travel has been finished """

        travelKey = self.helper.getInBusWithLicencePlate(self.userId, self.service, self.licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        directions = ["Z", "S", "other things"]
        for direction in directions:
            jsonResponse = self.helper.setDirection(travelKey, direction)

            self.assertEqual(jsonResponse['valid'], False)
            self.assertEqual(jsonResponse['message'], "Invalid direction.")

        self.helper.endRoute(travelKey)


