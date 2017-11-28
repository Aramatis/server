from django.test import TestCase
from django.utils import timezone

from AndroidRequests.models import Level, ScoreEvent, TranSappUser, ScoreHistory, EventRegistration
from AndroidRequests.statusResponse import Status
from AndroidRequests.tests.testHelper import TestHelper

import datetime as dt
import json


class ScoreTest(TestCase):

    def check_user_data(self, jsonScoreResponse, userObj, score):
        """ check user data given by url """
        self.assertEqual(jsonScoreResponse['userData']['id'], str(userObj.externalId))
        self.assertEqual(jsonScoreResponse['userData']['score'], score)
        self.assertIn("globalPosition", jsonScoreResponse['userData']['ranking'].keys())
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], userObj.level.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], userObj.level.maxScore)
        self.assertEqual(jsonScoreResponse['userData']['level']['minScore'], userObj.level.minScore)
        self.assertEqual(jsonScoreResponse['userData']['level']['position'], userObj.level.position)
        self.assertEqual(userObj.globalScore, score)


class EventScoreTest(ScoreTest):
    """ test score related with events """
    fixtures = ["levels", "scoreEvents"]

    def setUp(self):
        """ this method will automatically call for every single test """
        # create events
        self.test = TestHelper(self)
        self.test.insertEventsOnDatabase()
        self.eventBusCode = 'evn00201'

        self.score = ScoreEvent.objects.get(code=self.eventBusCode).score

        self.phoneId = '1df6e1b6a1b840d689b364119db3fb7c'
        licencePlate = 'AA1111'
        self.service = '507'
        self.machineId = self.test.askForMachineId(licencePlate)
        self.token = self.test.getInBusWithMachineId(self.phoneId, self.service, self.machineId)

        self.userId = '123456789'
        self.sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'

        user = self.test.createTranSappUsers(1)[0]
        user.userId = self.userId
        user.phoneId = self.phoneId
        user.sessionToken = self.sessionToken
        user.globalScore = 0
        user.save()
        self.assertIsNotNone(user.timeCreation)

    def test_calculateBusEventScoreWithoutParams(self):
        """This method test event score when the info is sending without params"""

        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId, self.service,
                                                     self.eventBusCode)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'], Status.getJsonStatus(Status.INVALID_PARAMS, {})['status'])
        self.assertEqual(jsonScoreResponse['message'], Status.getJsonStatus(Status.INVALID_PARAMS, {})['message'])
        self.assertNotIn("userData", jsonScoreResponse.keys())
        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_calculateBusEventScoreWithGoodParams(self):
        # report a bus event
        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, self.userId, self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.check_user_data(jsonScoreResponse, userObj, self.score)

        self.assertEqual(ScoreHistory.objects.first().score, self.score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

        # we will vote -1
        jsonResponse = self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                               self.service, self.eventBusCode,
                                                               EventRegistration.DECLINE, self.userId,
                                                               self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj.refresh_from_db()
        self.check_user_data(jsonScoreResponse, userObj, 2 * self.score)

        self.assertEqual(ScoreHistory.objects.count(), 2)

    def test_calculateBusEventScoreWithParamsButWrongUserId(self):
        wrongUserId = '987654321'

        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, wrongUserId, self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']

        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.INVALID_USER, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.INVALID_USER, {})['message'])

        self.assertNotIn("userData", jsonScoreResponse.keys())
        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_calculateBusEventScoreWithParamsButWrongSessionToken(self):
        wrongSessionToken = '3586b9f9-de09-4dca-99ee-892b803ac6e8'

        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, self.userId, wrongSessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']

        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['message'])

        self.assertNotIn("userData", jsonScoreResponse.keys())
        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_userPassToNextLevel(self):
        # increase score of event to pass level
        score = Level.objects.get(position=1).maxScore + 1
        ScoreEvent.objects.filter(code=self.eventBusCode). \
            update(score=score)

        # report a bus event
        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, self.userId, self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.check_user_data(jsonScoreResponse, userObj, score)
        self.assertEquals(userObj.level.position, 2)

        self.assertEqual(ScoreHistory.objects.first().score, score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

    def test_calculateBusStopEventScoreWithGoodParams(self):
        # insert bus stop
        stopCode = 'PA459'
        self.test.insertBusstopsOnDatabase([stopCode])
        eventStopCode = 'evn00010'
        score = ScoreEvent.objects.get(code=eventStopCode).score

        # report a bus event
        jsonResponse = self.test.reportStopEventByPost(self.phoneId, stopCode,
                                                       eventStopCode, self.userId, self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.check_user_data(jsonScoreResponse, userObj, score)

        self.assertEqual(ScoreHistory.objects.first().score, score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

        # we will vote -1
        jsonResponse = self.test.confirmOrDeclineStopEventByPost(self.phoneId, stopCode,
                                                                 eventStopCode, EventRegistration.DECLINE, self.userId,
                                                                 self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj.refresh_from_db()
        self.check_user_data(jsonScoreResponse, userObj, 2 * score)

        self.assertEqual(ScoreHistory.objects.count(), 2)


class DistanceScoreTest(ScoreTest):
    """ test score related with events """
    fixtures = ["scoreEvents"]

    def setUp(self):
        """  """
        self.test = TestHelper(self)

        self.phoneId = '1df6e1b6a1b840d689b364119db3fb7c'
        licencePlate = 'AA1111'
        self.service = '507'
        self.machineId = self.test.askForMachineId(licencePlate)
        self.token = self.test.getInBusWithMachineId(self.phoneId, self.service, self.machineId)

        self.userId = '123456789'
        self.sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'

        user = self.test.createTranSappUsers(1)[0]
        user.userId = self.userId
        user.phoneId = self.phoneId
        user.sessionToken = self.sessionToken
        user.globalScore = 0
        user.save()
        self.assertIsNotNone(user.timeCreation)

        self.eventCode = 'evn00300'

    def test_calculateDistanceScoreWithGoodParams(self):

        # send poses
        now = timezone.make_aware(dt.datetime.now())
        times = [now,
                 now + timezone.timedelta(0, 5),
                 now + timezone.timedelta(0, 10),
                 now + timezone.timedelta(0, 15),
                 now + timezone.timedelta(0, 20),
                 now + timezone.timedelta(0, 25),
                 now + timezone.timedelta(0, 30),
                 now + timezone.timedelta(0, 35),
                 now + timezone.timedelta(0, 40)]
        fTimes = []
        for time in times:
            fTimes.append(time.strftime("%Y-%m-%dT%X"))

        # distances between points: 
        # 0-1: 0.052 km
        # 1-2: 0.006 km
        # 2-3: 0.177 km
        # 3-4: 0.203 km
        # 4-5: 0.246 km
        # 5-6: 0.221 km
        # 6-7: 0.194 km
        # 7-8: 0.381 km
        poses = {"poses": [
            {"latitud": -33.458771, "longitud": -70.676266,
             "timeStamp": fTimes[0], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458699, "longitud": -70.675708,
             "timeStamp": fTimes[1], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.674678,
             "timeStamp": fTimes[2], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.673799,
             "timeStamp": fTimes[3], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458413, "longitud": -70.671631,
             "timeStamp": fTimes[4], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457983, "longitud": -70.669035,
             "timeStamp": fTimes[5], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457518, "longitud": -70.666718,
             "timeStamp": fTimes[6], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457196, "longitud": -70.664636,
             "timeStamp": fTimes[7], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457070, "longitud": -70.660559,
             "timeStamp": fTimes[8], "inVehicleOrNot": "vehicle"}
        ]
        }
        distances = [0.0523471429746, 0.0956726246579, 0.0814920031062, 0.202656182984, 0.245373794753, 0.220938698808,
                     0.196313468243, 0.378244108963]
        calculatedScore = round(reduce(lambda x,y: x+y, distances) * ScoreEvent.objects.get(code=self.eventCode).score, 8)

        jsonResponse = self.test.sendFakeTrajectoryOfToken(travelToken=self.token, poses=poses, userId=self.userId,
                                                           sessionToken=self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.check_user_data(jsonScoreResponse, userObj, calculatedScore)

        scoreHistoryObj = ScoreHistory.objects.first()
        self.assertEqual(scoreHistoryObj.scoreEvent.code, self.eventCode)
        self.assertEqual(scoreHistoryObj.score, calculatedScore)
        meta = json.loads(scoreHistoryObj.meta)
        self.assertEqual(meta["tripToken"], self.token)
        for index, pose in enumerate(meta["poses"]):
            self.assertEquals(pose["latitud"], poses["poses"][index]["latitud"])
            self.assertEquals(pose["longitud"], poses["poses"][index]["longitud"])
            self.assertEquals(pose["timeStamp"], poses["poses"][index]["timeStamp"])

    def test_calculateDistanceScoreWithGoodParamsAndPreviousPoints(self):

        # send poses
        now = timezone.make_aware(dt.datetime.now())
        times = [now,
                 now + timezone.timedelta(0, 5),
                 now + timezone.timedelta(0, 10),
                 now + timezone.timedelta(0, 15),
                 now + timezone.timedelta(0, 20),
                 now + timezone.timedelta(0, 25),
                 now + timezone.timedelta(0, 30),
                 now + timezone.timedelta(0, 35),
                 now + timezone.timedelta(0, 40)]
        fTimes = []
        for time in times:
            fTimes.append(time.strftime("%Y-%m-%dT%X"))

        # send first poses set
        # distances between points: 
        # 0-1: 0.052 km
        # 1-2: 0.006 km
        # 2-3: 0.177 km
        # 3-4: 0.203 km
        # 438 m
        poses1 = {"poses": [
            {"latitud": -33.458771, "longitud": -70.676266,
             "timeStamp": fTimes[0], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458699, "longitud": -70.675708,
             "timeStamp": fTimes[1], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.674678,
             "timeStamp": fTimes[2], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.673799,
             "timeStamp": fTimes[3], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458413, "longitud": -70.671631,
             "timeStamp": fTimes[4], "inVehicleOrNot": "vehicle"},
        ]
        }
        distances1 = [0.0523471429746, 0.0956726246579, 0.0814920031062, 0.202656182984]

        jsonResponse = self.test.sendFakeTrajectoryOfToken(travelToken=self.token,
                                                           poses=poses1, userId=self.userId,
                                                           sessionToken=self.sessionToken)
        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        # send second poses set
        # 4-5: 0.246 km
        # 5-6: 0.221 km
        # 6-7: 0.194 km
        # 7-8: 0.381 km
        # 1042 = 246 + 796
        poses2 = {"poses": [
            {"latitud": -33.457983, "longitud": -70.669035,
             "timeStamp": fTimes[5], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457518, "longitud": -70.666718,
             "timeStamp": fTimes[6], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457196, "longitud": -70.664636,
             "timeStamp": fTimes[7], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457070, "longitud": -70.660559,
             "timeStamp": fTimes[8], "inVehicleOrNot": "vehicle"}
        ]
        }
        distances2 = [0.220938698808, 0.196313468243, 0.378244108963]
        score = ScoreEvent.objects.get(code=self.eventCode).score
        calculatedScore1 = round(reduce(lambda x,y: x+y, distances1) * score, 8)
        distanceBetween = round(0.245373794753 * score, 8)
        calculatedScore2 = round(reduce(lambda x,y: x+y, distances2) * score, 8)
        calculatedScoreTotal = round(calculatedScore1 + distanceBetween + calculatedScore2, 8)

        userObj = TranSappUser.objects.first()
        self.check_user_data(jsonScoreResponse, userObj, calculatedScore1)

        jsonResponse = self.test.sendFakeTrajectoryOfToken(travelToken=self.token,
                                                           poses=poses2, userId=self.userId,
                                                           sessionToken=self.sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj.refresh_from_db()
        self.check_user_data(jsonScoreResponse, userObj, calculatedScoreTotal)

        self.assertEqual(ScoreHistory.objects.count(), 2)

        eventCode = 'evn00300'
        for scoreHistoryObj, calculatedScore, poses in zip(ScoreHistory.objects.all().order_by("id").iterator(),
                                                    [calculatedScore1, distanceBetween + calculatedScore2],
                                                    [poses1, poses2]):
            self.assertEqual(scoreHistoryObj.scoreEvent.code, eventCode)
            self.assertEqual(scoreHistoryObj.score, calculatedScore)
            meta = json.loads(scoreHistoryObj.meta)
            self.assertEqual(meta["tripToken"], self.token)
            for index, pose in enumerate(meta["poses"]):
                self.assertEquals(pose["latitud"], poses["poses"][index]["latitud"])
                self.assertEquals(pose["longitud"], poses["poses"][index]["longitud"])
                self.assertEquals(pose["timeStamp"], poses["poses"][index]["timeStamp"])
