import datetime as dt

from django.test import TransactionTestCase
from django.utils import timezone

from AndroidRequests.models import Level, ScoreEvent, TranSappUser, ScoreHistory
from AndroidRequests.statusResponse import Status
from AndroidRequests.tests.testHelper import TestHelper


# Create your tests here.

class EventScoreTest(TransactionTestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """
        # create events
        self.test = TestHelper(self)
        self.test.insertEventsOnDatabase()
        self.eventBusCode = 'evn00201'

        # create levels 
        Level.objects.create(name='level 1', minScore=0, maxScore=1000, position=1)
        Level.objects.create(name='level 2', minScore=1000, maxScore=2000, position=2)

        # create score event for eventCode
        self.score = 100
        ScoreEvent.objects.create(code=self.eventBusCode, score=self.score)

        self.phoneId = '1df6e1b6a1b840d689b364119db3fb7c'
        licencePlate = 'AA1111'
        self.service = '507'
        self.machineId = self.test.askForMachineId(licencePlate)
        self.token = self.test.getInBusWithMachineId(self.phoneId, self.service, self.machineId)

    def test_calculateBusEventScoreWithoutParams(self):
        '''This method test event score when the info is sending without params'''

        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId, self.service,
                                                     self.eventBusCode, '', '')

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'], 402)
        self.assertEqual(jsonScoreResponse['message'], 'invalid params')
        self.assertEqual(jsonScoreResponse['userData']['score'], -1)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], '')
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], '')

        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_calculateBusEventScoreWithGoodParams(self):

        # create TranSappUser
        userId = '123456789'
        sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=Level.objects.get(position=1), sessionToken=sessionToken)

        # report a bus event
        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, userId, sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.assertEqual(jsonScoreResponse['userData']['score'], self.score)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], userObj.level.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], userObj.level.maxScore)
        self.assertEqual(userObj.globalScore, self.score)

        self.assertEqual(ScoreHistory.objects.first().score, self.score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

        # we will vote -1
        jsonResponse = self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                               self.service, self.eventBusCode, 'decline', userId,
                                                               sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj.refresh_from_db()
        self.assertEqual(userObj.globalScore, 2 * self.score)
        self.assertEqual(jsonScoreResponse['userData']['score'], 2 * self.score)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], userObj.level.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], userObj.level.maxScore)

        self.assertEqual(ScoreHistory.objects.count(), 2)

    def test_calculateBusEventScoreWithParamsButWrongUserId(self):

        # create TranSappUser
        userId = '123456789'
        wrongUserId = '987654321'
        sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=Level.objects.get(position=1), sessionToken=sessionToken)

        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, wrongUserId, sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']

        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.INVALID_USER, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.INVALID_USER, {})['message'])

        self.assertEqual(jsonScoreResponse['userData']['score'], -1)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], '')
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], '')

        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_calculateBusEventScoreWithParamsButWrongSessionToken(self):

        # create TranSappUser
        userId = '123456789'
        sessionToken = 'd5dbd0ea-1dd5-4e0a-a8da-5a03e5e617d4'
        wrongSessionToken = '3586b9f9-de09-4dca-99ee-892b803ac6e8'
        TranSappUser.objects.create(userId=userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=Level.objects.get(position=1), sessionToken=sessionToken)
        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, userId, wrongSessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']

        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['message'])

        self.assertEqual(jsonScoreResponse['userData']['score'], -1)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], '')
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], '')

        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_userPassToNextLevel(self):

        # create TranSappUser
        userId = '123456789'
        sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=Level.objects.get(position=1), sessionToken=sessionToken)

        # increase score of event to pass level
        scoreEventObj = ScoreEvent.objects.first()
        scoreEventObj.score = 1001
        scoreEventObj.save()

        # report a bus event
        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventBusCode, userId, sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        nextLevel = Level.objects.get(position=2)

        userObj = TranSappUser.objects.first()
        self.assertEqual(jsonScoreResponse['userData']['score'], scoreEventObj.score)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], nextLevel.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], nextLevel.maxScore)
        self.assertEqual(userObj.globalScore, scoreEventObj.score)

        self.assertEqual(ScoreHistory.objects.first().score, scoreEventObj.score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

    def test_calculateBusStopEventScoreWithGoodParams(self):

        # insert bus stop
        stopCode = 'PA459'
        self.test.insertBusstopsOnDatabase([stopCode])
        eventStopCode = 'evn00010'
        score = 150
        ScoreEvent.objects.create(code=eventStopCode, score=score)

        # create TranSappUser
        userId = '123456789'
        sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=Level.objects.get(position=1), sessionToken=sessionToken)

        # report a bus event
        jsonResponse = self.test.reportStopEventByPost(self.phoneId, stopCode,
                                                       eventStopCode, userId, sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.assertEqual(jsonScoreResponse['userData']['score'], score)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], userObj.level.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], userObj.level.maxScore)
        self.assertEqual(userObj.globalScore, score)

        self.assertEqual(ScoreHistory.objects.first().score, score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

        # we will vote -1
        jsonResponse = self.test.confirmOrDeclineStopEventByPost(self.phoneId, stopCode,
                                                                 eventStopCode, 'decline', userId, sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj.refresh_from_db()
        self.assertEqual(userObj.globalScore, 2 * score)
        self.assertEqual(jsonScoreResponse['userData']['score'], 2 * score)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], userObj.level.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], userObj.level.maxScore)

        self.assertEqual(ScoreHistory.objects.count(), 2)

    def test_calculateDistanceScoreWithGoodParams(self):

        # there is a user inside the bus (setup)

        # create event score
        score = 100
        eventCode = 'evn00300'
        ScoreEvent.objects.create(code=eventCode, score=score)

        # create TranSappUser
        userId = '123456789'
        sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=Level.objects.get(position=1), sessionToken=sessionToken)

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
        calculatedScore = 147.30380245

        jsonResponse = self.test.sendFakeTrajectoryOfToken(travelToken=self.token,
                                                           poses=poses, userId=userId, sessionToken=sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.assertEqual(jsonScoreResponse['userData']['score'], calculatedScore)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], userObj.level.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], userObj.level.maxScore)
        self.assertEqual(userObj.globalScore, calculatedScore)

        self.assertEqual(ScoreHistory.objects.first().scoreEvent.code, eventCode)
        self.assertEqual(ScoreHistory.objects.first().score, calculatedScore)
        # self.assertEqual(json.loads(ScoreHistory.objects.first().meta), poses)

    def test_calculateDistanceScoreWithGoodParamsAndPreviousPoints(self):

        # there is a user inside the bus (setup)

        # create event score
        score = 100
        eventCode = 'evn00300'
        ScoreEvent.objects.create(code=eventCode, score=score)

        # create TranSappUser
        userId = '123456789'
        sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=Level.objects.get(position=1), sessionToken=sessionToken)

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

        jsonResponse = self.test.sendFakeTrajectoryOfToken(travelToken=self.token,
                                                           poses=poses1, userId=userId, sessionToken=sessionToken)
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
        calculatedScore1 = 43.21679537
        calculatedScore2 = 104.08700708
        calculatedScoreTotal = 147.30380245

        jsonResponse = self.test.sendFakeTrajectoryOfToken(travelToken=self.token,
                                                           poses=poses2, userId=userId, sessionToken=sessionToken)

        jsonScoreResponse = jsonResponse['gamificationData']
        self.assertEqual(jsonScoreResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonScoreResponse['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        userObj = TranSappUser.objects.first()
        self.assertEqual(jsonScoreResponse['userData']['score'], calculatedScoreTotal)
        self.assertEqual(jsonScoreResponse['userData']['level']['name'], userObj.level.name)
        self.assertEqual(jsonScoreResponse['userData']['level']['maxScore'], userObj.level.maxScore)
        self.assertEqual(userObj.globalScore, calculatedScoreTotal)

        self.assertEqual(ScoreHistory.objects.count(), 2)
        scoreHistoryObj = ScoreHistory.objects.all()

        self.assertEqual(scoreHistoryObj[0].scoreEvent.code, eventCode)
        self.assertEqual(scoreHistoryObj[0].score, calculatedScore1)
        # self.assertEqual(json.loads(ScoreHistory.objects.first().meta), poses)

        self.assertEqual(scoreHistoryObj[1].scoreEvent.code, eventCode)
        self.assertEqual(scoreHistoryObj[1].score, calculatedScore2)
        # self.assertEqual(json.loads(ScoreHistory.objects.first().meta), poses)
