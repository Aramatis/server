from django.test import TestCase
from django.utils import timezone

from AndroidRequests.models import ActiveToken, Level, Token
from AndroidRequests.tests.testHelper import TestHelper

import AndroidRequests.cronTasks as cronTasks
import uuid


class CronTasksTestCase(TestCase):
    """ test for cron-task actions """

    def setUp(self):
        self.phone_id = str(uuid.uuid4())
        self.route = '506'
        self.license_plate = 'XXYY25'

        self.helper = TestHelper(self)

    def test_clean_expired_active_token(self):

        # token requested. Simulate that request was asked double of time
        # defined in MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS ago
        delta = cronTasks.MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS * 2
        timestamp = timezone.now() - timezone.timedelta(minutes=delta)

        token = self.helper.getInBusWithLicencePlate(self.phone_id, self.route, self.license_plate, timestamp)

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 0)
        self.assertEqual(Token.objects.first().purgeCause, Token.SERVER_DOES_NOT_RECEIVE_LOCATIONS)

    def test_keep_active_token(self):
        timestamp = timezone.now()

        token = self.helper.getInBusWithLicencePlate(
            self.phone_id, self.route, self.license_plate, timestamp)

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)

        self.helper.sendFakeTrajectoryOfToken(token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)
        self.assertIsNone(Token.objects.first().purgeCause)


class CronTasksWithUserTestCase(TestCase):
    """ test for cron-task actions with session users """
    fixtures = ["scoreEvents", "levels"]

    def setUp(self):
        self.phone_id = str(uuid.uuid4())
        self.route = '506'
        self.license_plate = 'XXYY25'

        self.helper = TestHelper(self)

        self.user = self.helper.createTranSappUsers(1)[0]
        self.user.globalScore = 0
        self.user.save()

        self.token = self.helper.getInBusWithLicencePlateByPost(
            self.phone_id, self.route, self.license_plate, user_id=self.user.userId,
            session_token=str(self.user.sessionToken))
        # timeCreation of token
        self.now = timezone.now() - timezone.timedelta(minutes=cronTasks.MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS * 2)

    def test_remove_score_because_distance(self):
        """ remove score won because distance is less than 100 meters and time greater than 1 minute """

        times = [self.now,
                 self.now + timezone.timedelta(minutes=5)]
        format_times = [time.strftime("%Y-%m-%dT%X") for time in times]

        # distance is like 60 meters app.
        poses = {"poses": [
            {"latitud": -33.457187, "longitud": -70.664014,
             "timeStamp": format_times[0], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.45708, "longitud": -70.663542,
             "timeStamp": format_times[1], "inVehicleOrNot": "vehicle"}
            ]
        }
        self.helper.sendFakeTrajectoryOfToken(self.token, poses, self.user.userId, self.user.sessionToken)

        # evaluate trip
        self.helper.evaluateTrip(self.token, 4, self.user.userId, self.user.sessionToken)

        # check score was updated
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.globalScore, 0)

        # clean token and run evaluate score
        ActiveToken.objects.update(timeStamp=self.now)
        cronTasks.cleanActiveTokenTable()

        # distance is less than 100 meters so not points
        self.assertEquals(ActiveToken.objects.count(), 0)
        self.user.refresh_from_db()
        self.assertEquals(self.user.globalScore, 0)

    def test_remove_score_because_time(self):
        """ remove score won because time is less than 1 minute """

        times = [self.now,
                 self.now + timezone.timedelta(seconds=59)]
        format_times = [time.strftime("%Y-%m-%dT%X") for time in times]

        # distance is like 60 meters app.
        poses = {"poses": [
            {"latitud": -33.457187, "longitud": -70.664014,
             "timeStamp": format_times[0], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.456936, "longitud": -70.660688,
             "timeStamp": format_times[1], "inVehicleOrNot": "vehicle"}
            ]
        }
        self.helper.sendFakeTrajectoryOfToken(self.token, poses, self.user.userId, self.user.sessionToken)

        # check score was updated
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.globalScore, 0)

        # clean token and run evaluate score
        ActiveToken.objects.update(timeStamp=self.now)
        cronTasks.cleanActiveTokenTable()

        # time is less than 1 minute so not points
        self.assertEquals(ActiveToken.objects.count(), 0)
        self.user.refresh_from_db()
        self.assertEquals(self.user.globalScore, 0)

    def test_remove_score_and_decrease_level(self):
        """ remove score won because time is less than 1 minute and reduce level """

        times = [self.now,
                 self.now + timezone.timedelta(seconds=59)]
        format_times = [time.strftime("%Y-%m-%dT%X") for time in times]

        # distance is like 60 meters app.
        poses = {"poses": [
            {"latitud": -33.457187, "longitud": -70.664014,
             "timeStamp": format_times[0], "inVehicleOrNot": "vehicle"},
            {"latitud": -33.456936, "longitud": -70.660688,
             "timeStamp": format_times[1], "inVehicleOrNot": "vehicle"}
        ]
        }
        self.helper.sendFakeTrajectoryOfToken(self.token, poses, self.user.userId, self.user.sessionToken)

        # set user score to global score in min score of level 2 and user is in level 2
        level_obj = Level.objects.get(position=2)
        self.user.level = level_obj
        self.user.globalScore = level_obj.minScore
        self.user.save()

        # clean token and run evaluate score
        ActiveToken.objects.update(timeStamp=self.now)
        cronTasks.cleanActiveTokenTable()

        # user changed level to level 1
        self.user.refresh_from_db()
        self.assertEquals(self.user.level.position, 1)
