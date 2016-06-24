from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

# python stuf
import json

# model
from AndroidRequests.models import ActiveToken, Event
# view
from AndroidRequests.allviews.RequestToken import RequestToken
# functions to test
import AndroidRequests.cronTasks as cronTasks

class CronTasksTestCase(TestCase):
    """ test for cron-task actions """
    def setUp(self):
        self.userId = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.busService = '506'
        self.registrationPlate = 'XXYY25'

        factory = RequestFactory()

        urlBase = '/android/requestToken'

        self.request = factory.get(urlBase)
        self.request.user = AnonymousUser()
        self.responseView = RequestToken()

    def test_clean_expired_active_token(self):

        # token requested. Simulate that request was asked double of time
        # defined in MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS ago
        delta = cronTasks.MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS*2
        timeStamp = timezone.now()-timezone.timedelta(minutes=delta)
        response = self.responseView.get(self.request, self.userId, self.busService, self.registrationPlate, timeStamp)
        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.all().first().token_id, token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 0)

    def test_keep_active_token(self):
        timeStamp = timezone.now()
        response = self.responseView.get(self.request, self.userId, self.busService, self.registrationPlate, timeStamp)
        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.all().first().token_id, token)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.all().first().token_id, token)

