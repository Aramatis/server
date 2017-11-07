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

        userQuantity = 100
        self.helper.createTranSappUsers(userQuantity)

        # simulate a report to execute update of global positions
        score = ScoreEvent.objects.create(code="111", score=100)
        ScoreHistory.objects.create(tranSappUser_id=TranSappUser.objects.first().id, scoreEvent=score,
                                    timeCreation=timezone.now())

    def testGlobalPositionCrontabWithScoreEvent(self):
        """ test method used by crontab to reorder users based on globalScore updating globalPosition """

        # change global position
        TranSappUser.objects.update(globalPosition=-1)

        cronTasks.updateGlobalRanking()

        # check global position
        previousScore = None
        previousPosition = None
        for user in TranSappUser.objects.all().order_by("-globalScore"):
            if previousScore is None:
                previousScore = user.globalScore
                previousPosition = user.globalPosition
                continue
            if user.globalScore < previousScore:
                self.assertEquals(user.globalPosition, previousPosition + 1)
            else:
                self.assertEquals(user.globalPosition, previousPosition)
            previousPosition = user.globalPosition
            previousScore = user.globalScore

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
