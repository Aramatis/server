from django.test import TransactionTestCase
from django.utils import timezone

from AndroidRequests.models import Busv2, Busassignment, Event, EventForBusv2
from AndroidRequests.tests.testHelper import TestHelper

import AndroidRequests.constants as constants


class BusEventTest(TransactionTestCase):
    """ test for bus events """
    fixtures = ["events"]

    def setUp(self):
        """ this method will automatically call for every single test """
        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.route = '507'
        self.stop_code = 'PA459'

        self.test = TestHelper(self)
        self.test.insertServicesOnDatabase([self.route])
        self.test.insertBusstopsOnDatabase([self.stop_code])

    def test_EventsByBusWithDummyLicensePlate(self):
        """This method test the bus with a dummy license plate """

        license_plate = constants.DUMMY_LICENSE_PLATE
        self.test.getInBusWithLicencePlateByPost(self.phone_id, self.route, license_plate)
        event_id = 'evn00202'

        # submitting one event to the server
        json_response = self.test.reportEvent(
            self.phone_id, self.route, license_plate, event_id)

        self.assertEqual(json_response['registrationPlate'], license_plate)
        self.assertEqual(json_response['service'], self.route)
        self.assertEqual(len(json_response['events']), 1)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

    def test_EventsByBus(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific bus"""

        license_plate = 'AA0000'
        event_id = 'evn00202'
        self.test.getInBusWithLicencePlateByPost(
            self.phone_id, self.route, license_plate)

        # submitting one event to the server
        json_response = self.test.reportEvent(
            self.phone_id, self.route, license_plate, event_id)

        self.assertEqual(json_response['registrationPlate'], license_plate)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

        # ===================================================================================
        # do event +1 to the event
        json_response = self.test.confirmOrDeclineEvent(
            self.phone_id, self.route, license_plate, event_id, EventForBusv2.CONFIRM)

        self.assertEqual(json_response['registrationPlate'], license_plate)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 2)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

        # do event -1 to the event
        json_response = self.test.confirmOrDeclineEvent(
            self.phone_id, self.route, license_plate, event_id, EventForBusv2.DECLINE)

        self.assertEqual(json_response['registrationPlate'], license_plate)
        self.assertEqual(json_response['events'][0]['eventDecline'], 1)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 2)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

        # ask for events
        json_response = self.test.requestEventsForBus(
            self.route, license_plate)

        self.assertEqual(json_response['registrationPlate'], license_plate)
        self.assertEqual(json_response['events'][0]['eventDecline'], 1)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 2)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

        # change manually the timeStamp to simulate an event that has expired
        bus = Busv2.objects.get(registrationPlate=license_plate)
        busassignment = Busassignment.objects.get(uuid=bus, service=self.route)
        event = Event.objects.get(id=event_id)
        event_for_bus_obj = EventForBusv2.objects.get(busassignment=busassignment, event=event)

        event_for_bus_obj.timeStamp = event_for_bus_obj.timeStamp - timezone.timedelta(minutes=event.lifespam)
        event_for_bus_obj.timeCreation = event_for_bus_obj.timeCreation - timezone.timedelta(minutes=event.lifespam)
        event_for_bus_obj.expireTime = event_for_bus_obj.expireTime - timezone.timedelta(minutes=event.lifespam)
        event_for_bus_obj.save()

        # ask for events and the answer should be none
        json_response = self.test.reportEvent(
            self.phone_id, self.route, license_plate, event_id)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

    def test_AskForEventsOfNonExistentBus(self):
        # ask for events for a bus that does not exists
        license_plate = 'AABB00'

        json_response = self.test.requestEventsForBus(
            self.route, license_plate)

        self.assertEqual(len(json_response['events']), 0)
        self.assertEqual(json_response['registrationPlate'], license_plate)
        self.assertEqual(json_response['service'], self.route)
