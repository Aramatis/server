from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json

# my stuff
from AndroidRequests.models import *
# views
from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.SendPoses import SendPoses
import AndroidRequests.views as views
import AndroidRequests.constants as Constants
from AndroidRequests.tests.testHelper import TestHelper

# Create your tests here.

class BusEventTest(TestCase):
    """ test for bus events """

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.service = '507'
        self.stop = 'PA459'

        self.test = TestHelper(self)
        self.test.insertEventsOnDatabase()
        self.test.insertServicesOnDatabase([self.service])
        self.test.insertBusstopsOnDatabase([self.stop])

    def test_EventsByBusWithDummyLicensePlate(self):
        '''This method test the bus with a dummy license plate '''

        licencePlate = Constants.DUMMY_LICENSE_PLATE
        self.test.getInBusWithLicencePlate(self.userId, self.service, licencePlate)
        eventCode = 'evn00101'

        # submitting one event to the server
        jsonResponse = self.test.reportEvent(self.userId, self.service, licencePlate, eventCode)

        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['service'], self.service)
        self.assertEqual(len(jsonResponse['events']), 1)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

    def test_EventsByNonExistentBus(self):
        '''This method test to make a report for a bus that not exists in the database '''

        licencePlate = 'AA0000'
        eventCode = 'evn00101'

        # submitting one event to the server
        jsonResponse = self.test.reportEvent(self.userId, self.service, licencePlate, eventCode)
        self.assertEqual(len(jsonResponse['events']), 1)

    def test_EventsByBus(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific bus'''

        licencePlate = 'AA0000'
        eventCode = 'evn00101'
        self.test.getInBusWithLicencePlate(self.userId, self.service, licencePlate)

        # submitting one event to the server
        jsonResponse = self.test.reportEvent(self.userId, self.service, licencePlate, eventCode)

        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # do event +1 to the event
        jsonResponse = self.test.confirmOrDeclineEvent(self.userId, self.service, licencePlate, eventCode, 'confirm')

        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # do event -1 to the event
        jsonResponse = self.test.confirmOrDeclineEvent(self.userId, self.service, licencePlate, eventCode, 'decline')

        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # ask for events
        jsonResponse = self.test.requestEventsForBus(self.service, licencePlate)
        
        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # change manually the timeStamp to simulate an event that has expired
        bus = Busv2.objects.get(registrationPlate=licencePlate)
        busassignment = Busassignment.objects.get(uuid=bus, service=self.service)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusv2.objects.get(busassignment=busassignment,event=event)

        anEvent.timeStamp = anEvent.timeCreation - timezone.timedelta(minutes=event.lifespam)
        anEvent.save()

        # ask for ecents and the answere should be none
        jsonResponse = self.test.reportEvent(self.userId, self.service, licencePlate, eventCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'],eventCode)
