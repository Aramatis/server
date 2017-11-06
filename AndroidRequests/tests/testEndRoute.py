from django.test import TestCase

import AndroidRequests.constants as Constants
from AndroidRequests.tests.testHelper import TestHelper


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

    def test_endRouteWithInvalidActiveToken(self):
        """ finish unactive travel """

        travelKey = self.helper.getInBusWithLicencePlateByPost(
            self.phoneId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        self.helper.endRoute(travelKey)

        jsonResponse = self.helper.endRoute(travelKey)

        self.assertEqual(jsonResponse['response'], 'Token doesn\'t exist.')
