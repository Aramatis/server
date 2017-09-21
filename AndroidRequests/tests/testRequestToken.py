from django.test import TestCase

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import ActiveToken, PoseInTrajectoryOfToken, Token, Busv2

import AndroidRequests.constants as Constants


class RequestTokenTest(TestCase):
    """ test for request token url """

    def setUp(self):
        """ this method will automatically call for every single test """
        self.helper = TestHelper(self)
        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.licencePlate = 'AA1111'
        self.route = '507'
        self.machineId = self.helper.askForMachineId(self.licencePlate)

    def test_RequestTokenV2WithRealLicencePlateAndTranSappUser(self):
        """ This method will test to ask a token with transapp user data """

        user = self.helper.createTranSappUsers(1)[0]

        testToken = self.helper.getInBusWithMachineIdByPost(
            self.phoneId, self.route, self.machineId, None, None, user.userId, user.sessionToken)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=testToken, token__tranSappUser=user).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken, tranSappUser=user).exists(), True)

        jsonResponse = self.helper.endRoute(testToken)
        self.assertEqual(jsonResponse['response'], 'Trip ended.')

    def test_RequestTokenV2WithRealLicencePlateAndFakeTranSappUser(self):
        """ This method will test to ask a token with fake transapp user data """

        user = self.helper.createTranSappUsers(1)[0]

        # userId is None
        testToken = self.helper.getInBusWithMachineIdByPost(
            self.phoneId, self.route, self.machineId, None, None, None, user.sessionToken)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=testToken, token__tranSappUser=None).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken, tranSappUser=None).exists(), True)

        jsonResponse = self.helper.endRoute(testToken)
        self.assertEqual(jsonResponse['response'], 'Trip ended.')

    def test_RequestTokenV2WithRealLicencePlateAndPosition(self):
        """ This method will test to ask a token with transapp user data and check that latitude and longitude sent
            was saved """
        busLatitude = -33.456973
        busLongitude = -70.663947

        testToken = self.helper.getInBusWithMachineIdByPost(
            self.phoneId, self.route, self.machineId, busLongitude, busLatitude)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.all().exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)
        self.assertEqual(PoseInTrajectoryOfToken.objects.filter(token__token=testToken).count(), 1)

        jsonResponse = self.helper.endRoute(testToken)
        self.assertEqual(jsonResponse['response'], 'Trip ended.')

    def test_RequestTokenWithDummyLicensePlateUUID(self):
        """ This method will test a token for a dummy license plate bus with uuid """

        licencePlate = Constants.DUMMY_LICENSE_PLATE

        # a ghost bus is created with the same uuid that was received
        self.assertEqual(Busv2.objects.filter(uuid=self.machineId).exists(), True)

        testToken = self.helper.getInBusWithMachineId(
            self.phoneId, self.route, self.machineId)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)

        jsonResponse = self.helper.endRoute(testToken)
        self.assertEqual(jsonResponse['response'], 'Trip ended.')

    def test_RequestTokenV2WithRealLicencePlate(self):
        """ This method will test a token for bus with uuid """

        # a ghost bus is created with the same uuid that was recieved
        self.assertEqual(Busv2.objects.filter(uuid=self.machineId).exists(), True)

        testToken = self.helper.getInBusWithMachineId(
            self.phoneId, self.route, self.machineId)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)

        jsonResponse = self.helper.endRoute(testToken)
        self.assertEqual(jsonResponse['response'], 'Trip ended.')
