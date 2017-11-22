from django.test import TestCase
from django.utils import timezone

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status

from onlinegps.models import LastGPS

import uuid


class SendTrajectoryV2Test(TestCase):
    """ test for end route url """
    fixtures = ["scoreEvents"]

    def setUp(self):
        """ this method will automatically call for every single test """
        self.helper = TestHelper(self)

        self.phoneId = str(uuid.uuid4())
        self.route = "507"
        self.licensePlate = "CJRB74"

        self.helper.insertServicesOnDatabase([self.route])
        self.user = self.helper.createTranSappUsers(1)[0]
        self.user.globalScore = 0
        self.user.save()

    def test_send_trajectory_where_token_does_not_exist(self):
        """ token does not exist """
        fakeToken = "fake_token"
        jsonResponse = self.helper.sendFakeTrajectoryOfTokenV2(fakeToken)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['message'])

        self.assertEquals(PoseInTrajectoryOfToken.objects.count(), 0)

    def test_send_trajectory_without_locations(self):
        """ send trajectory """
        tripToken = self.helper.getInBusWithLicencePlateByPost(self.phoneId, self.route, self.licensePlate)
        poses = {"poses": []}
        jsonResponse = self.helper.sendFakeTrajectoryOfTokenV2(tripToken, poses)

        self.assertEqual(jsonResponse['status'],
                         Status.getJsonStatus(Status.TRAJECTORY_DOES_NOT_HAVE_LOCATIONS, {})['status'])
        self.assertEqual(jsonResponse['message'],
                         Status.getJsonStatus(Status.TRAJECTORY_DOES_NOT_HAVE_LOCATIONS, {})['message'])

        self.assertEquals(PoseInTrajectoryOfToken.objects.count(), 0)

    def test_send_trajectory_ok_without_user(self):
        """ send trajectory """
        tripToken = self.helper.getInBusWithLicencePlateByPost(self.phoneId, self.route, self.licensePlate)
        jsonResponse = self.helper.sendFakeTrajectoryOfTokenV2(tripToken)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.OK, {})['message'])

        self.assertEquals(PoseInTrajectoryOfToken.objects.count(), 9)

    def test_send_trajectory_ok_with_user(self):
        """ send trajectory """
        tripToken = self.helper.getInBusWithLicencePlateByPost(
            self.phoneId, self.route, self.licensePlate, userId=self.user.userId, sessionToken=self.user.sessionToken)
        jsonResponse = self.helper.sendFakeTrajectoryOfTokenV2(tripToken, userId=self.user.userId,
                                                               sessionToken=self.user.sessionToken)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.OK, {})['message'])


    def test_send_trajectory_with_get_off_response(self):
        """ send trajectory """
        now = timezone.now()
        # distance between points is greater than 500 meters
        locations = [
            (-70.664046,-33.457106),
            (-70.676224,-33.458655)
        ]
        LastGPS.objects.create(licensePlate=self.licensePlate, userRouteCode="{0}I".format(self.route), timestamp=now,
                               longitude=locations[0][0], latitude=locations[0][1])

        tripToken = self.helper.getInBusWithLicencePlateByPost(
            self.phoneId, self.route, self.licensePlate, userId=self.user.userId, sessionToken=self.user.sessionToken)
        poses = {"poses": [{
                "longitude": locations[1][0],
                "latitude": locations[1][1],
                "timeDelay": -2300,
                "inVehicleOrNot": True
            }]
        }
        jsonResponse = self.helper.sendFakeTrajectoryOfTokenV2(tripToken, poses, userId=self.user.userId,
                                                               sessionToken=self.user.sessionToken)
        
        self.assertEqual(jsonResponse['status'], 
                         Status.getJsonStatus(Status.USER_BUS_IS_FAR_AWAY_FROM_REAL_BUS, {})['status'])
        self.assertEqual(jsonResponse['message'], 
                         Status.getJsonStatus(Status.USER_BUS_IS_FAR_AWAY_FROM_REAL_BUS, {})['message'])