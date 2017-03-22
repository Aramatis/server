from django.test import TestCase
from django.utils import timezone

# model
from AndroidRequests.models import ActiveToken
# view
from AndroidRequests.tests.testHelper import TestHelper
# functions to test
import AndroidRequests.cronTasks as cronTasks


class CronTasksTestCase(TestCase):
    """ test for cron-task actions """

    def setUp(self):
        self.userId = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.busService = '506'
        self.registrationPlate = 'XXYY25'

        self.helper = TestHelper(self)

    def test_clean_expired_active_token(self):

        # token requested. Simulate that request was asked double of time
        # defined in MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS ago
        delta = cronTasks.MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS * 2
        timeStamp = timezone.now() - timezone.timedelta(minutes=delta)

        token = self.helper.getInBusWithLicencePlate(
            self.userId, self.busService, self.registrationPlate, timeStamp)

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 0)

    def test_keep_active_token(self):
        timeStamp = timezone.now()

        token = self.helper.getInBusWithLicencePlate(
            self.userId, self.busService, self.registrationPlate, timeStamp)

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.first().token.token, token)
