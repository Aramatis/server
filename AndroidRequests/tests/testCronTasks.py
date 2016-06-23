from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
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
        pass

    def test_clean_expired_active_token(self):

        factory = RequestFactory()

        urlBase = '/android/requestToken'
        userId = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        busService = '506'
        registrationPlate = 'XXYY25'

        request = factory.get(urlBase)
        request.user = AnonymousUser()
        responseView = RequestToken()

        # first token requested. Simulate that request was asked double of time
        # defined in MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS ago
        delta = cronTasks.MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS*2
        firstTimeStamp = timezone.now()-timezone.timedelta(minutes=delta)
        firstResponse = responseView.get(request, userId, busService, registrationPlate, firstTimeStamp)
        firstJsonResponse = json.loads(firstResponse.content)
        firstToken = firstJsonResponse['token']

        self.assertEqual(firstResponse.status_code, 200)
        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.all().first().token_id, firstToken)

        # second token requested
        secondTimeStamp = timezone.now()
        secondResponse = responseView.get(request, userId, busService, registrationPlate, secondTimeStamp)
        secondJsonResponse = json.loads(secondResponse.content)
        secondToken = secondJsonResponse['token']

        self.assertEqual(secondResponse.status_code, 200)
        self.assertEqual(ActiveToken.objects.count(), 2)
        self.assertEqual(ActiveToken.objects.all().last().token_id, secondToken)

        cronTasks.cleanActiveTokenTable()

        self.assertEqual(ActiveToken.objects.count(), 1)
        self.assertEqual(ActiveToken.objects.all().first().token_id, secondToken)

    def test_clear_events(self):
        self.eventBusStop = Event.objects.create(id='ebs', name='event for bus stop', \
                description='event for bus stop from bus stop', eventType='busStop', origin='o', lifespam='30')
        self.eventBusFromBusStop = Event.objects.create(id='bfbs', name='event for bus', \
                description='event for bus from bus stop', eventType='bus', origin='o', lifespam='5')
        self.eventBusFromBus = Event.objects.create(id='bfb', name='event for bus', \
                description='event for bus from bus', eventType='bus', origin='i', lifespam='5')
        pass
