from django.test import TransactionTestCase
from django.utils import timezone

from gtfs.models import GTFS, BusStop
from AndroidRequests.models import EventRegistration
from AndroidRequests.tests.testHelper import TestHelper


class BusStopEventTestCase(TransactionTestCase):
    """ test the behavior of events when busstops are updated """
    fixtures = ["events"]

    # TERMINAR ESTO!!!!!! EL TEST; HACER LA URL; CAMBIAR LA SESION Y LISTO
    def setUp(self):
        """ this method will automatically call for every single test """

        self.stop_code = 'PA459'

        self.test = TestHelper(self)
        self.test.insertBusstopsOnDatabase([self.stop_code])

        # report bus stop event
        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.event_id = 'evn00010'

        json_response = self.test.reportStopEvent(self.phone_id, self.stop_code, self.event_id)

        self.assertEqual(json_response['codeBusStop'], self.stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], self.event_id)

        self.newGtfsVersion = 'v0.8'
        GTFS.objects.create(version=self.newGtfsVersion, timeCreation=timezone.now())

        # add new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            self.test.insertBusstopsOnDatabase([self.stop_code])

        self.assertEqual(BusStop.objects.count(), 2)

    def test_AskEventThroughNewBusStopVersion(self):
        # ask bus stop events with new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            json_response = self.test.requestEventsForBusStop(self.stop_code)

        self.assertEqual(json_response['codeBusStop'], self.stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], self.event_id)

    def test_confirmEventOfpreviousBusStopversion(self):
        # ask bus stop events with new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            json_response = self.test.confirmOrDeclineStopEvent(
                self.phone_id, self.stop_code, self.event_id, EventRegistration.CONFIRM)

        self.assertEqual(json_response['codeBusStop'], self.stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 2)
        self.assertEqual(json_response['events'][0]['eventcode'], self.event_id)

    def test_declineEventOfpreviousBusStopversion(self):
        # ask bus stop events with new bus stop version
        with self.settings(GTFS_VERSION=self.newGtfsVersion):
            json_response = self.test.confirmOrDeclineStopEvent(
                self.phone_id, self.stop_code, self.event_id, EventRegistration.DECLINE)

        self.assertEqual(json_response['codeBusStop'], self.stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 1)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], self.event_id)
