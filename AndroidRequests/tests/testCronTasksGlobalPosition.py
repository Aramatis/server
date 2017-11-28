from django.test import TestCase
from django.utils import timezone

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import TranSappUser, ScoreHistory, ScoreEvent

import AndroidRequests.cronTasks as cronTasks
import datetime


class CronTasksTestCase(TestCase):
    """ test for cron-task actions """

    def setUp(self):
        self.helper = TestHelper(self)

        user_quantity = 100
        self.helper.createTranSappUsers(user_quantity)

        # simulate a report to execute update of global positions
        score_obj = ScoreEvent.objects.create(code="111", score=100)
        ScoreHistory.objects.create(tranSappUser_id=TranSappUser.objects.first().id, scoreEvent=score_obj,
                                    timeCreation=timezone.now())

    def testGlobalPositionCrontabWithScoreEvent(self):
        """ test method used by crontab to reorder users based on globalScore updating globalPosition """

        # change global position
        TranSappUser.objects.update(globalPosition=-1)

        cronTasks.updateGlobalRanking()

        # check global position
        previous_score = None
        previous_position = None
        for user in TranSappUser.objects.all().order_by("-globalScore"):
            if previous_score is None:
                previous_score = user.globalScore
                previous_position = user.globalPosition
                continue
            if user.globalScore < previous_score:
                self.assertEquals(user.globalPosition, previous_position + 1)
            else:
                self.assertEquals(user.globalPosition, previous_position)
            previous_position = user.globalPosition
            previous_score = user.globalScore

    def testGlobalPositionCrontabWithoutScoreEvent(self):
        """ test method used by crontab to reorder users based on globalScore updating globalPosition but without
        score event inside MINUTE_DELTA minutes, so globalPosition does not change """

        ScoreHistory.objects.update(
            timeCreation=(timezone.now() - datetime.timedelta(minutes=cronTasks.MINUTE_DELTA * 2)))
        # change global position
        TranSappUser.objects.update(globalPosition=-1)

        # it does not do anything because there is not scoreEvent in history
        cronTasks.updateGlobalRanking()

        # check global position
        for user in TranSappUser.objects.all().order_by("-globalScore"):
            self.assertEquals(user.globalPosition, -1)
