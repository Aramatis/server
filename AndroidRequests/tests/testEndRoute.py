from django.test import TestCase

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import Token, ActiveToken

import AndroidRequests.constants as constants
import uuid


class EndRouteTest(TestCase):
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

        json_response = self.helper.endRoute(travel_key)

        self.assertEqual(json_response['response'], 'Trip ended.')
        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertIsNone(Token.objects.first().purgeCause)

    def test_endRouteWithInvalidActiveToken(self):
        """ finish unactive travel """

        travel_key = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.route, constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travel_key)

        self.helper.endRoute(travel_key)

        json_response = self.helper.endRoute(travel_key)

        self.assertEqual(json_response['response'], 'Token doesn\'t exist.')
        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertIsNone(Token.objects.first().purgeCause)


class EndRouteWithUserTest(TestCase):
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

        self.helper.endRoute(travel_key)

        self.user.refresh_from_db()
        self.assertTrue(old_score > self.user.globalScore)

        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertIsNone(Token.objects.first().purgeCause)
