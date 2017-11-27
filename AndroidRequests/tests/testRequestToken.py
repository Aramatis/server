from django.test import TestCase

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import ActiveToken, PoseInTrajectoryOfToken, Token, Busv2

import AndroidRequests.constants as constants


class RequestTokenTest(TestCase):
    """ test for request token url """

    def setUp(self):
        """ this method will automatically call for every single test """
        self.helper = TestHelper(self)
        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.license_plate = 'AA1111'
        self.route = '507'
        self.machine_id = self.helper.askForMachineId(self.license_plate)

    def test_RequestTokenV2WithRealLicencePlateAndTranSappUser(self):
        """ This method will test to ask a token with transapp user data """

        user = self.helper.createTranSappUsers(1)[0]

        test_token = self.helper.getInBusWithMachineIdByPost(
            self.phone_id, self.route, self.machine_id, None, None, user.userId, user.sessionToken)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=test_token, token__tranSappUser=user).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=test_token, tranSappUser=user).exists(), True)

        json_response = self.helper.endRoute(test_token)
        self.assertEqual(json_response['response'], 'Trip ended.')

    def test_RequestTokenV2WithRealLicencePlateAndFakeTranSappUser(self):
        """ This method will test to ask a token with fake transapp user data """

        user = self.helper.createTranSappUsers(1)[0]

        # userId is None
        test_token = self.helper.getInBusWithMachineIdByPost(
            self.phone_id, self.route, self.machine_id, None, None, None, user.sessionToken)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(token__token=test_token, token__tranSappUser=None).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=test_token, tranSappUser=None).exists(), True)

        json_response = self.helper.endRoute(test_token)
        self.assertEqual(json_response['response'], 'Trip ended.')

    def test_RequestTokenV2WithRealLicencePlateAndPosition(self):
        """ This method will test to ask a token with transapp user data and check that latitude and longitude sent
            was saved """
        bus_latitude = -33.456973
        bus_longitude = -70.663947

        test_token = self.helper.getInBusWithMachineIdByPost(
            self.phone_id, self.route, self.machine_id, bus_longitude, bus_latitude)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.all().exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=test_token).exists(), True)
        self.assertEqual(PoseInTrajectoryOfToken.objects.filter(token__token=test_token).count(), 1)

        json_response = self.helper.endRoute(test_token)
        self.assertEqual(json_response['response'], 'Trip ended.')

    def test_RequestTokenV2WithDummyLicensePlateUUID(self):
        """ This method will test a token for a dummy license plate bus with uuid """
        license_plate = constants.DUMMY_LICENSE_PLATE

        # a ghost bus is created with the same uuid that was received
        self.assertEqual(Busv2.objects.filter(uuid=self.machine_id).exists(), True)

        test_token = self.helper.getInBusWithLicencePlate(self.phone_id, self.route, license_plate)

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token__token=test_token).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=test_token).exists(), True)

        json_response = self.helper.endRoute(test_token)
        self.assertEqual(json_response['response'], 'Trip ended.')

    def test_RequestTokenV2WithRealLicencePlate(self):
        """ This method will test a token for bus with uuid """

        # a ghost bus is created with the same uuid that was received
        self.assertEqual(Busv2.objects.filter(uuid=self.machine_id).exists(), True)

        test_token = self.helper.getInBusWithMachineId(self.phone_id, self.route, self.machine_id)

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token__token=test_token).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=test_token).exists(), True)

        json_response = self.helper.endRoute(test_token)
        self.assertEqual(json_response['response'], 'Trip ended.')
