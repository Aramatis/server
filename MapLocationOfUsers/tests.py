from django.test import TestCase, RequestFactory, Client
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

from MapLocationOfUsers.views import MapHandler, GetMapPositions, GetMapTrajectory
from AndroidRequests.models import DevicePositionInTime, PoseInTrajectoryOfToken
from AndroidRequests.tests.testHelper import TestHelper

import json
import datetime
import uuid


class GetMapPositionsTest(TestCase):

    def setUp(self):
        self.phoneId = uuid.uuid4()
        self.phoneId2 = uuid.uuid4()

        self.helper = TestHelper(self)

        points = [
            [self.phoneId, 3 , 4, (timezone.now() - datetime.timedelta(minutes=2))],
            [self.phoneId, 5 , 6, (timezone.now() - datetime.timedelta(minutes=1))],
            [self.phoneId, 7 , 8, timezone.now()],
            [self.phoneId2, 3 , 4, (timezone.now() - datetime.timedelta(minutes=2))],
            [self.phoneId2, 5 , 6, (timezone.now() - datetime.timedelta(minutes=1))],
            [self.phoneId2, 7 , 8, timezone.now()],
        ]
        for point in points:
            DevicePositionInTime.objects.create(
                phoneId=point[0],
                longitude=point[1],
                latitude=point[2],
                timeStamp=point[3])
            DevicePositionInTime.objects.create(
                phoneId=point[0],
                longitude=point[1],
                latitude=point[2],
                timeStamp=point[3])

        self.factory = RequestFactory()

    def test_getPositions(self):
        """This test the response of the current poses"""
        url = "/map/activeuserpose"
        response = Client(url).get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertEqual(len(data), 2)
        for posititionRes in data:
            self.assertEqual(posititionRes['longitud'], 7)
            self.assertEqual(posititionRes['latitud'], 8)

    def test_showMap(self):
        """this test is for testing the response of the map view"""
        url = "/map/show"
        response = Client(url).get(url)

        self.assertEqual(response.status_code, 200)

    def test_getGetMapTrajectory(self):
        """this test the trajectory that the server gives to the map. """

        timeStampNow = str(timezone.localtime(timezone.now()))
        timeStampNow = timeStampNow[0:19]
        testPoses = {"poses": [
            {"latitud": -33.458771,
             "longitud": -70.676266,
             "timeStamp": str(timeStampNow),
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458699,
             "longitud": -70.675708,
             "timeStamp": "2017-10-01T18:10:10",
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646,
             "longitud": -70.674678,
             "timeStamp": "2017-10-01T18:10:15",
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646,
             "longitud": -70.673799,
             "timeStamp": "2017-10-01T18:10:20",
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458413,
             "longitud": -70.671631,
             "timeStamp": "2017-10-01T18:10:24",
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457983,
             "longitud": -70.669035,
             "timeStamp": "2017-10-01T18:10:30",
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457518,
             "longitud": -70.666718,
             "timeStamp": "2017-10-01T18:10:35",
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457196,
             "longitud": -70.664636,
             "timeStamp": "2017-10-01T18:10:40",
             "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457070,
             "longitud": -70.660559,
             "timeStamp": str(timeStampNow),
             "inVehicleOrNot": "vehicle"}]}

        buses_number = 6
        testTokens = []

        for cont in range(buses_number):
            testToken = self.helper.getInBusWithLicencePlateByPost(self.phoneId, "503", "ZZZZ00")
            testTokens.append(testToken)

        # save last token
        timeOutToken = testTokens[-1]

        for cont in range(buses_number):
            self.helper.sendFakeTrajectoryOfToken(testTokens[cont], testPoses)

        nonTrajectory = PoseInTrajectoryOfToken.objects.filter(
            token__token=timeOutToken)
        for data in nonTrajectory:
            data.timeStamp = data.timeStamp - timezone.timedelta(minutes=61)
            data.save()

        url = "/map/activetrajectory"
        response = Client().get(url)

        responseMessage = json.loads(response.content)

        # all tokens given by GetMapTrajectory are different of timeOutToken
        # and its positions is the most recent
        for aMsg in responseMessage:
            print(aMsg)
            self.assertTrue(aMsg['token'] != timeOutToken)
            self.assertEqual(aMsg["lastPose"][1], -70.676266)
            self.assertEqual(aMsg["lastPose"][0], -33.458771)

        self.assertEqual(len(responseMessage), len(testTokens) - 1)
