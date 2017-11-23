from django.test import TestCase

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import Token, ActiveToken

import AndroidRequests.constants as Constants
import uuid


class EndRouteTest(TestCase):
    """ test for end route url """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.helper = TestHelper(self)

        self.service = '507'
        self.licencePlate = 'PABJ45'

        self.helper.insertServicesOnDatabase([self.service])

    def test_endRouteWithValidActiveToken(self):
        """ finish active travel """

        travelKey = self.helper.getInBusWithLicencePlateByPost(
            self.phoneId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        jsonResponse = self.helper.endRoute(travelKey)

        self.assertEqual(jsonResponse['response'], 'Trip ended.')
        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertIsNone(Token.objects.first().purgeCause)

    def test_endRouteWithInvalidActiveToken(self):
        """ finish unactive travel """

        travelKey = self.helper.getInBusWithLicencePlateByPost(
            self.phoneId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        self.helper.endRoute(travelKey)

        jsonResponse = self.helper.endRoute(travelKey)

        self.assertEqual(jsonResponse['response'], 'Token doesn\'t exist.')
        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertIsNone(Token.objects.first().purgeCause)


class EndRouteWithUserTest(TestCase):
    """ test for end route url """
    fixtures = ["scoreEvents"]

    def setUp(self):
        """ this method will automatically call for every single test """
        self.helper = TestHelper(self)

        self.phoneId = str(uuid.uuid4())
        self.service = '507'
        self.licencePlate = 'PABJ45'

        self.helper.insertServicesOnDatabase([self.service])
        self.user = self.helper.createTranSappUsers(1)[0]
        self.user.globalScore = 0
        self.user.save()

    def test_endRouteWithValidActiveToken(self):
        """ finish active travel """
        travelKey = self.helper.getInBusWithLicencePlateByPost(
            self.phoneId, self.service, self.licencePlate, userId=self.user.userId, sessionToken=self.user.sessionToken)
        self.helper.sendFakeTrajectoryOfToken(travelKey, userId=self.user.userId, sessionToken=self.user.sessionToken)

        self.user.refresh_from_db()
        oldScore = self.user.globalScore

        self.helper.endRoute(travelKey)

        self.user.refresh_from_db()
        self.assertTrue(oldScore > self.user.globalScore)

        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertIsNone(Token.objects.first().purgeCause)