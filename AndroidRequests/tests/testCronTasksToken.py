from django.test import TestCase
from django.utils import timezone

from AndroidRequests.models import ActiveToken
from AndroidRequests.tests.testHelper import TestHelper

import AndroidRequests.cronTasks as cronTasks


class CronTasksTestCase(TestCase):
    """ test for cron-task actions """

    def setUp(self):
        self.phoneId = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.route = '506'
        self.licensePlate = 'XXYY25'

        self.helper = TestHelper(self)

    def test_clean_expired_active_token(self):

        # token requested. Simulate that request was asked double of time
        # defined in MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS ago
        delta = cronTasks.MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS * 2
        timeStamp = timezone.now() - timezone.timedelta(minutes=delta)

        token = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.route, self.licensePlate, timeStamp)

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 0)

    def test_keep_active_token(self):
        timeStamp = timezone.now()

        token = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.route, self.licensePlate, timeStamp)

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)

        self.helper.sendFakeTrajectoryOfToken(token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)
