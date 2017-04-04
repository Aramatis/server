from django.test import TransactionTestCase
from django.utils import timezone
from django.conf import settings

# my stuff
from AndroidRequests.models import DevicePositionInTime, BusStop, Service, ServiceStopDistance, ServiceLocation, ActiveToken, Token, EventForBusStop, Event, Busv2, Busassignment, GTFS
# test helper
from AndroidRequests.tests.testHelper import TestHelper

# Create your tests here.


class BusStopEventTestCase(TransactionTestCase):
    """ test the behavior of events when busstops are updated """

    # TERMINAR ESTO!!!!!! EL TEST; HACER LA URL; CAMBIAR LA SESION Y LISTO
    def setUp(self):
        """ this method will automatically call for every single test """

        self.busStopCode = 'PA459'

        self.test = TestHelper(self)

        self.test.insertEventsOnDatabase()
        self.test.insertBusstopsOnDatabase([self.busStopCode])

        # report bus stop event
        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.eventCode = 'evn00010'
       
        jsonResponse = self.test.reportStopEvent(self.phoneId, self.busStopCode, self.eventCode) 

        self.assertEqual(jsonResponse['codeBusStop'], self.busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.eventCode)

        self.newGtfsVersion = 'v0.8'
        GTFS.objects.create(version=self.newGtfsVersion, timeCreation=timezone.now())

        # add new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            self.test.insertBusstopsOnDatabase([self.busStopCode])
            #busstopv08 = BusStop.objects.get(gtfs__version=settings.GTFS_VERSION)
            #busstopv08.name = 'new bus stop'
            #busstopv08.save()

        self.assertEqual(BusStop.objects.count(), 2)

    def test_AskEventThroughNewBusStopVersion(self):

        # ask bus stop events with new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            jsonResponse = self.test.requestEventsForBusStop(self.busStopCode)

        self.assertEqual(jsonResponse['codeBusStop'], self.busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.eventCode)

    def test_confirmEventOfpreviousBusStopversion(self):

        # ask bus stop events with new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            jsonResponse = self.test.confirmOrDeclineStopEvent(
                self.phoneId, self.busStopCode, self.eventCode, 'confirm')

        self.assertEqual(jsonResponse['codeBusStop'], self.busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.eventCode)

    def test_declineEventOfpreviousBusStopversion(self):

        # ask bus stop events with new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            jsonResponse = self.test.confirmOrDeclineStopEvent(
                self.phoneId, self.busStopCode, self.eventCode, 'decline')

        self.assertEqual(jsonResponse['codeBusStop'], self.busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.eventCode)

