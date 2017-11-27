from django.test import TestCase
from django.utils import timezone, dateparse

from AndroidRequests.models import Level, ScoreEvent, TranSappUser, ScoreHistory, EventRegistration
from AndroidRequests.statusResponse import Status
from AndroidRequests.tests.testHelper import TestHelper

import json


class ScoreTest(TestCase):
    def check_user_data(self, json_score_response, user_obj, score):
        """ check user data given by url """
        self.assertEqual(json_score_response['userData']['id'], str(user_obj.externalId))
        self.assertEqual(json_score_response['userData']['score'], score)
        self.assertIn("globalPosition", json_score_response['userData']['ranking'].keys())
        self.assertEqual(json_score_response['userData']['level']['name'], user_obj.level.name)
        self.assertEqual(json_score_response['userData']['level']['maxScore'], user_obj.level.maxScore)
        self.assertEqual(json_score_response['userData']['level']['minScore'], user_obj.level.minScore)
        self.assertEqual(json_score_response['userData']['level']['position'], user_obj.level.position)
        self.assertEqual(user_obj.globalScore, score)


class EventScoreTest(ScoreTest):
    """ test score related with events """
    fixtures = ["events", "levels", "scoreEvents"]

    def setUp(self):
        """ this method will automatically call for every single test """
        # create events
        self.test = TestHelper(self)
        self.event_bus_code = 'evn00201'

        self.score = ScoreEvent.objects.get(code=self.event_bus_code).score

        self.phone_id = '1df6e1b6a1b840d689b364119db3fb7c'
        license_plate = 'AA1111'
        self.route = '507'
        self.machine_id = self.test.askForMachineId(license_plate)
        self.token = self.test.getInBusWithMachineId(self.phone_id, self.route, self.machine_id)

        self.user_id = '123456789'
        self.session_token = '4951e324-9ab4-4f1f-845c-04259785b58b'

        user = self.test.createTranSappUsers(1)[0]
        user.userId = self.user_id
        user.phoneId = self.phone_id
        user.sessionToken = self.session_token
        user.globalScore = 0
        user.save()
        self.assertIsNotNone(user.timeCreation)

    def test_calculateBusEventScoreWithoutParams(self):
        """This method test event score when the info is sending without params"""

        json_response = self.test.reportEventV2ByPost(self.phone_id, self.machine_id, self.route, self.event_bus_code)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'], Status.getJsonStatus(Status.INVALID_PARAMS, {})['status'])
        self.assertEqual(json_score_response['message'], Status.getJsonStatus(Status.INVALID_PARAMS, {})['message'])
        self.assertNotIn("userData", json_score_response.keys())
        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_calculateBusEventScoreWithGoodParams(self):
        # report a bus event
        json_response = self.test.reportEventV2ByPost(self.phone_id, self.machine_id, self.route, self.event_bus_code,
                                                      self.user_id, self.session_token)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        user_obj = TranSappUser.objects.first()
        self.check_user_data(json_score_response, user_obj, self.score)

        self.assertEqual(ScoreHistory.objects.first().score, self.score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

        # we will vote -1
        json_response = self.test.confirmOrDeclineEventV2ByPost(self.phone_id, self.machine_id, self.route,
                                                                self.event_bus_code, EventRegistration.DECLINE,
                                                                self.user_id, self.session_token)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        user_obj.refresh_from_db()
        self.check_user_data(json_score_response, user_obj, 2 * self.score)

        self.assertEqual(ScoreHistory.objects.count(), 2)

    def test_calculateBusEventScoreWithParamsButWrongUserId(self):
        wrong_user_id = '987654321'

        json_response = self.test.reportEventV2ByPost(self.phone_id, self.machine_id, self.route, self.event_bus_code,
                                                      wrong_user_id, self.session_token)

        json_score_response = json_response['gamificationData']

        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.INVALID_USER, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.INVALID_USER, {})['message'])

        self.assertNotIn("userData", json_score_response.keys())
        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_calculateBusEventScoreWithParamsButWrongSessionToken(self):
        wrong_session_token = '3586b9f9-de09-4dca-99ee-892b803ac6e8'

        json_response = self.test.reportEventV2ByPost(self.phone_id, self.machine_id, self.route, self.event_bus_code,
                                                      self.user_id, wrong_session_token)

        json_score_response = json_response['gamificationData']

        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['message'])

        self.assertNotIn("userData", json_score_response.keys())
        self.assertEqual(ScoreHistory.objects.count(), 0)

    def test_userPassToNextLevel(self):
        # increase score of event to pass level
        score = Level.objects.get(position=1).maxScore + 1
        ScoreEvent.objects.filter(code=self.event_bus_code).update(score=score)

        # report a bus event
        json_response = self.test.reportEventV2ByPost(self.phone_id, self.machine_id, self.route, self.event_bus_code,
                                                      self.user_id, self.session_token)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        user_obj = TranSappUser.objects.first()
        self.check_user_data(json_score_response, user_obj, score)
        self.assertEquals(user_obj.level.position, 2)

        self.assertEqual(ScoreHistory.objects.first().score, score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

    def test_calculateBusStopEventScoreWithGoodParams(self):
        # insert bus stop
        stop_code = 'PA459'
        self.test.insertBusstopsOnDatabase([stop_code])
        event_stop_code = 'evn00010'
        score = ScoreEvent.objects.get(code=event_stop_code).score

        # report a bus event
        json_response = self.test.reportStopEventByPost(self.phone_id, stop_code,
                                                        event_stop_code, self.user_id, self.session_token)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        user_obj = TranSappUser.objects.first()
        self.check_user_data(json_score_response, user_obj, score)

        self.assertEqual(ScoreHistory.objects.first().score, score)
        self.assertEqual(ScoreHistory.objects.first().meta, None)

        # we will vote -1
        json_response = self.test.confirmOrDeclineStopEventByPost(self.phone_id, stop_code, event_stop_code,
                                                                  EventRegistration.DECLINE, self.user_id,
                                                                  self.session_token)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        user_obj.refresh_from_db()
        self.check_user_data(json_score_response, user_obj, 2 * score)

        self.assertEqual(ScoreHistory.objects.count(), 2)


class DistanceScoreTest(ScoreTest):
    """ test score related with events """
    fixtures = ["scoreEvents"]

    def setUp(self):
        """  """
        self.test = TestHelper(self)

        self.phone_id = '1df6e1b6a1b840d689b364119db3fb7c'
        license_plate = 'AA1111'
        self.route = '507'
        self.machine_id = self.test.askForMachineId(license_plate)
        self.token = self.test.getInBusWithMachineId(self.phone_id, self.route, self.machine_id)

        self.user_id = '123456789'
        self.session_token = '4951e324-9ab4-4f1f-845c-04259785b58b'

        user = self.test.createTranSappUsers(1)[0]
        user.userId = self.user_id
        user.phoneId = self.phone_id
        user.sessionToken = self.session_token
        user.globalScore = 0
        user.save()
        self.assertIsNotNone(user.timeCreation)

        self.eventCode = 'evn00300'

    def test_calculateDistanceScoreWithGoodParams(self):

        # send poses
        now = timezone.now()
        times = [now,
                 now + timezone.timedelta(0, 5),
                 now + timezone.timedelta(0, 10),
                 now + timezone.timedelta(0, 15),
                 now + timezone.timedelta(0, 20),
                 now + timezone.timedelta(0, 25),
                 now + timezone.timedelta(0, 30),
                 now + timezone.timedelta(0, 35),
                 now + timezone.timedelta(0, 40)]
        formatted_times = []
        for time in times:
            formatted_times.append(time.strftime("%Y-%m-%dT%X"))

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
             "timeStamp": formatted_times[0], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458699, "longitud": -70.675708,
             "timeStamp": formatted_times[1], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.674678,
             "timeStamp": formatted_times[2], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.673799,
             "timeStamp": formatted_times[3], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458413, "longitud": -70.671631,
             "timeStamp": formatted_times[4], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457983, "longitud": -70.669035,
             "timeStamp": formatted_times[5], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457518, "longitud": -70.666718,
             "timeStamp": formatted_times[6], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457196, "longitud": -70.664636,
             "timeStamp": formatted_times[7], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457070, "longitud": -70.660559,
             "timeStamp": formatted_times[8], "inVehicleOrNot": "vehicle"}
        ]
        }
        distances = [0.0523471429746, 0.0956726246579, 0.0814920031062, 0.202656182984, 0.245373794753, 0.220938698808,
                     0.196313468243, 0.378244108963]
        calculated_score = round(reduce(lambda x, y: x + y, distances) *
                                 ScoreEvent.objects.get(code=self.eventCode).score, 8)

        json_response = self.test.sendFakeTrajectoryOfToken(travel_token=self.token, poses=poses, user_id=self.user_id,
                                                            session_token=self.session_token)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        user_obj = TranSappUser.objects.first()
        self.check_user_data(json_score_response, user_obj, calculated_score)

        score_history_obj = ScoreHistory.objects.first()
        self.assertEqual(score_history_obj.scoreEvent.code, self.eventCode)
        self.assertEqual(score_history_obj.score, calculated_score)
        meta = json.loads(score_history_obj.meta)
        self.assertEqual(meta["token"], self.token)
        for index, pose in enumerate(meta["poses"]):
            self.assertEquals(pose[0], poses["poses"][index]["longitud"])
            self.assertEquals(pose[1], poses["poses"][index]["latitud"])
            self.assertEquals(dateparse.parse_datetime(pose[2]),
                              timezone.make_aware(dateparse.parse_datetime(poses["poses"][index]["timeStamp"])))

    def test_calculateDistanceScoreWithGoodParamsAndPreviousPoints(self):

        # send poses
        now = timezone.now()
        times = [now,
                 now + timezone.timedelta(0, 5),
                 now + timezone.timedelta(0, 10),
                 now + timezone.timedelta(0, 15),
                 now + timezone.timedelta(0, 20),
                 now + timezone.timedelta(0, 25),
                 now + timezone.timedelta(0, 30),
                 now + timezone.timedelta(0, 35),
                 now + timezone.timedelta(0, 40)]
        formatted_times = []
        for time in times:
            formatted_times.append(time.strftime("%Y-%m-%dT%X"))

        # send first poses set
        # distances between points: 
        # 0-1: 0.052 km
        # 1-2: 0.006 km
        # 2-3: 0.177 km
        # 3-4: 0.203 km
        # 438 m
        poses1 = {"poses": [
            {"latitud": -33.458771, "longitud": -70.676266,
             "timeStamp": formatted_times[0], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458699, "longitud": -70.675708,
             "timeStamp": formatted_times[1], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.674678,
             "timeStamp": formatted_times[2], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458646, "longitud": -70.673799,
             "timeStamp": formatted_times[3], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.458413, "longitud": -70.671631,
             "timeStamp": formatted_times[4], "inVehicleOrNot": "vehicle"},
        ]
        }
        distances1 = [0.0523471429746, 0.0956726246579, 0.0814920031062, 0.202656182984]

        json_response = self.test.sendFakeTrajectoryOfToken(travel_token=self.token,
                                                            poses=poses1, user_id=self.user_id,
                                                            session_token=self.session_token)
        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        # send second poses set
        # 4-5: 0.246 km
        # 5-6: 0.221 km
        # 6-7: 0.194 km
        # 7-8: 0.381 km
        # 1042 = 246 + 796
        poses2 = {"poses": [
            {"latitud": -33.457983, "longitud": -70.669035,
             "timeStamp": formatted_times[5], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457518, "longitud": -70.666718,
             "timeStamp": formatted_times[6], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457196, "longitud": -70.664636,
             "timeStamp": formatted_times[7], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.457070, "longitud": -70.660559,
             "timeStamp": formatted_times[8], "inVehicleOrNot": "vehicle"}
        ]
        }
        distances2 = [0.220938698808, 0.196313468243, 0.378244108963]
        score = ScoreEvent.objects.get(code=self.eventCode).score
        calculated_score1 = round(reduce(lambda x, y: x + y, distances1) * score, 8)
        distance_between = round(0.245373794753 * score, 8)
        calculated_score2 = round(reduce(lambda x, y: x + y, distances2) * score, 8)
        calculated_score_total = round(calculated_score1 + distance_between + calculated_score2, 8)

        user_obj = TranSappUser.objects.first()
        self.check_user_data(json_score_response, user_obj, calculated_score1)

        json_response = self.test.sendFakeTrajectoryOfToken(travel_token=self.token,
                                                            poses=poses2, user_id=self.user_id,
                                                            session_token=self.session_token)

        json_score_response = json_response['gamificationData']
        self.assertEqual(json_score_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_score_response['message'],
                         Status.getJsonStatus(Status.OK, {})['message'])

        user_obj.refresh_from_db()
        self.check_user_data(json_score_response, user_obj, calculated_score_total)

        self.assertEqual(ScoreHistory.objects.count(), 2)

        event_code = 'evn00300'
        for score_history_obj, calculated_score, poses in zip(ScoreHistory.objects.all().order_by("id").iterator(),
                                                              [calculated_score1, distance_between + calculated_score2],
                                                              [poses1, poses2]):
            self.assertEqual(score_history_obj.scoreEvent.code, event_code)
            self.assertEqual(score_history_obj.score, calculated_score)
            meta = json.loads(score_history_obj.meta)
            self.assertEqual(meta["token"], self.token)
            for index, pose in enumerate(meta["poses"]):
                self.assertEquals(pose[0], poses["poses"][index]["longitud"])
                self.assertEquals(pose[1], poses["poses"][index]["latitud"])
                self.assertEquals(dateparse.parse_datetime(pose[2]),
                                  timezone.make_aware(dateparse.parse_datetime(poses["poses"][index]["timeStamp"])))
