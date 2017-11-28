from django.test import TestCase

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import Token, ActiveToken
from AndroidRequests.statusResponse import Status

import AndroidRequests.constants as constants
import uuid


class EndRouteByPostTest(TestCase):
    """ test for end route url """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.helper = TestHelper(self)

        self.route = '507'
        self.license_plate = 'PABJ45'

        self.helper.insertServicesOnDatabase([self.route])

    def test_endRouteWithValidActiveToken(self):
        """ finish active travel """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.route, constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travel_key)

        json_response = self.helper.endRouteByPost(travel_key, Token.USER_SAYS_GET_OFF)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertEqual(Token.objects.first().purgeCause, Token.USER_SAYS_GET_OFF)

    def test_endRouteWithInvalidActiveToken(self):
        """ finish inactive travel """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.route, constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travel_key)

        self.helper.endRouteByPost(travel_key, Token.SERVER_SAYS_GET_OFF)

        json_response = self.helper.endRouteByPost(travel_key, Token.USER_SAYS_GET_OFF)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['status'])
        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertEqual(Token.objects.first().purgeCause, Token.SERVER_SAYS_GET_OFF)


class EndRouteByPostWithUserTest(TestCase):
    """ test for end route url """
    fixtures = ["scoreEvents"]

    def setUp(self):
        """ this method will automatically call for every single test """
        self.helper = TestHelper(self)

        self.phone_id = str(uuid.uuid4())
        self.route = '507'
        self.license_plate = 'PABJ45'

        self.helper.insertServicesOnDatabase([self.route])
        self.user = self.helper.createTranSappUsers(1)[0]
        self.user.globalScore = 0
        self.user.save()

    def test_endRouteWithValidActiveToken(self):
        """ finish active travel """
        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.route, self.license_plate, user_id=self.user.userId, session_token=self.user.sessionToken)
        self.helper.sendFakeTrajectoryOfToken(travel_key, user_id=self.user.userId, session_token=self.user.sessionToken)

        self.user.refresh_from_db()
        old_score = self.user.globalScore

        self.helper.endRouteByPost(travel_key, Token.USER_SAYS_GET_OFF)

        self.user.refresh_from_db()
        self.assertTrue(old_score > self.user.globalScore)
        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertEqual(Token.objects.first().purgeCause, Token.USER_SAYS_GET_OFF)
