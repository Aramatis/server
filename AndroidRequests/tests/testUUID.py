from django.contrib.auth.models import AnonymousUser
from django.test import TransactionTestCase, RequestFactory
from django.utils import timezone

from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RegisterEventBusV2 import RegisterEventBusV2
from AndroidRequests.allviews.RequestTokenV2 import RequestTokenV2
from AndroidRequests.models import Busv2, ActiveToken, Token, Busassignment, Event, EventForBusv2, EventForBusStop
from AndroidRequests.tests.testHelper import TestHelper

import AndroidRequests.constants as Constants
import json
import re


class DummyLicensePlateUUIDTest(TransactionTestCase):
    fixtures = ["events"]

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.phone_id2 = "4f20c8f4-ddea-4c6c-87bb-c7bd3d435a51"

        # loads the events
        self.helper = TestHelper(self)

        # add dummy  bus
        self.license_plate = "AA1111"
        self.route = "507"

        self.machineId = self.helper.askForMachineId(self.license_plate)
        self.helper.getInBusWithMachineId(
            self.phone_id, self.route, self.machineId)

        # add dummy bus stop
        stop_code = "PA459"
        self.helper.insertBusstopsOnDatabase([stop_code])

        # add dummy service and its patha
        self.route = "507"
        self.direction = "I"
        self.helper.insertServicesOnDatabase([self.route])

        self.helper.insertServiceStopDistanceOnDatabase([stop_code])
        self.helper.insertServiceLocationOnDatabase([self.route + self.direction])

    def test_EventsByBusWithDummyLicensePlateUUID(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific dummy bus"""

        license_plate = Constants.DUMMY_LICENSE_PLATE
        route = "507"
        event_id = "evn00202"

        machine_id = self.helper.askForMachineId(license_plate)

        # a ghost bus is created with the same uuid that was recieved
        self.assertEqual(Busv2.objects.filter(uuid=machine_id).exists(), True)

        test_token = self.helper.getInBusWithMachineId(
            self.phone_id, route, machine_id)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=test_token).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=test_token).exists(), True)
        # the created token has the uuid for the dummybus
        # self.assertEqual(Token.objects.filter(uuid=puuid).exists(), True)

        # submitting one event to the server
        json_response = self.helper.reportEventV2(
            self.phone_id, machine_id, route, event_id)

        self.assertEqual(json_response["uuid"], machine_id)
        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 0)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 1)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        # ===================================================================================
        # getting events for a specific bus
        json_response = self.helper.requestEventsForBusV2(machine_id)

        # verify the previous event reported
        self.assertEqual(json_response["uuid"], machine_id)
        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 0)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 1)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        # ===================================================================================
        # do event +1 to the event
        json_response = self.helper.confirmOrDeclineEventV2(self.phone_id, machine_id, route,
                                                            event_id, EventForBusv2.CONFIRM)

        self.assertEqual(json_response["uuid"], machine_id)
        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 0)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 2)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        # ===================================================================================
        # getting events for a specific bus
        json_response = self.helper.requestEventsForBusV2(machine_id)

        # verify the previous event reported
        self.assertEqual(json_response["uuid"], machine_id)
        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 0)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 2)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        # do event -1 to the event
        json_response = self.helper.confirmOrDeclineEventV2(self.phone_id, machine_id, route,
                                                            event_id, EventForBusv2.DECLINE)

        self.assertEqual(json_response["uuid"], machine_id)
        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 1)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 2)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        # ===================================================================================
        # getting events for a specific bus
        json_response = self.helper.requestEventsForBusV2(machine_id)

        # verify the previous event reported
        self.assertEqual(json_response["uuid"], machine_id)
        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 1)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 2)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        # change manually the timeStamp to simulate an event that has expired
        bus_obj = Busv2.objects.get(uuid=machine_id)
        bus_assignment_obj = Busassignment.objects.get(service=route, uuid=bus_obj)
        event_obj = Event.objects.get(id=event_id)
        event_for_bus_obj = EventForBusv2.objects.get(
            busassignment=bus_assignment_obj, event=event_obj)

        time_delta = timezone.timedelta(minutes=event_obj.lifespam)
        event_for_bus_obj.expireTime = event_for_bus_obj.timeCreation - time_delta
        event_for_bus_obj.save()

        # ask for events and the answer should be none
        json_response = self.helper.requestEventsForBusV2(machine_id)

        self.assertEqual(len(json_response["events"]), 0)

    def test_EventsByBusv2(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific bus"""

        license_plate = "AA1111"
        route = "507"
        event_id = "evn00202"

        machine_id = self.helper.askForMachineId(license_plate)

        # submitting one event to the server
        json_response = self.helper.reportEventV2(self.phone_id, machine_id, route, event_id)

        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 0)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 1)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        # ===================================================================================
        # getting events for a specific bus
        request_to_request_event_for_bus = self.factory.get(
            "/android/requestEventsForBus/v2/")
        request_to_request_event_for_bus.user = AnonymousUser()

        # verify the previous event reported
        request_event_for_bus_view = EventsByBusV2()
        response_to_request_event_for_bus = request_event_for_bus_view.get(request_to_request_event_for_bus,
                                                                           machine_id)

        response_to_request_event_for_bus = json.loads(
            response_to_request_event_for_bus.content)

        self.assertEqual(response_to_request_event_for_bus[
                             "registrationPlate"], license_plate)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventcode"], event_id)

        # ===================================================================================
        # do event +1 to the event
        json_response = self.helper.confirmOrDeclineEventV2(
            self.phone_id, machine_id, route, event_id, EventForBusv2.CONFIRM)

        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 0)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 2)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        response_to_request_event_for_bus = request_event_for_bus_view.get(request_to_request_event_for_bus,
                                                                           machine_id)
        response_to_request_event_for_bus = json.loads(
            response_to_request_event_for_bus.content)

        self.assertEqual(response_to_request_event_for_bus[
                             "registrationPlate"], license_plate)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventConfirm"], 2)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventcode"], event_id)

        # do event -1 to the event
        json_response = self.helper.confirmOrDeclineEventV2(
            self.phone_id, machine_id, route, event_id, EventForBusStop.DECLINE)

        self.assertEqual(json_response["registrationPlate"], license_plate)
        self.assertEqual(json_response["events"][0]["eventDecline"], 1)
        self.assertEqual(json_response["events"][0]["eventConfirm"], 2)
        self.assertEqual(json_response["events"][0]["eventcode"], event_id)

        response_to_request_event_for_bus = request_event_for_bus_view.get(request_to_request_event_for_bus,
                                                                           machine_id)
        response_to_request_event_for_bus = json.loads(
            response_to_request_event_for_bus.content)

        self.assertEqual(response_to_request_event_for_bus[
                             "registrationPlate"], license_plate)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventDecline"], 1)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventConfirm"], 2)
        self.assertEqual(response_to_request_event_for_bus[
                             "events"][0]["eventcode"], event_id)

        # change manually the timeStamp to simulate an event that has expired
        # bus= Bus.objects.get(registrationPlate=license_plate, service=route)
        bus_obj = Busv2.objects.get(registrationPlate=license_plate)
        bus_assignment_obj = Busassignment.objects.get(uuid=bus_obj, service=route)
        event_obj = Event.objects.get(id=event_id)
        event_for_bus_obj = EventForBusv2.objects.get(
            busassignment=bus_assignment_obj, event=event_obj)

        time_delta = timezone.timedelta(minutes=event_obj.lifespam)
        event_for_bus_obj.expireTime = event_for_bus_obj.timeCreation - time_delta
        event_for_bus_obj.save()

        # ask for events and the answer should be none
        response_to_request_event_for_bus = request_event_for_bus_view.get(
            request_to_request_event_for_bus, bus_obj.uuid)
        response_to_request_event_for_bus = json.loads(
            response_to_request_event_for_bus.content)

        self.assertEqual(len(response_to_request_event_for_bus["events"]), 0)

    def test_EventsByBusStopv2(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific busStop"""

        stop_code = "PA459"
        event_id = "evn00001"
        # submitting some events to the server
        request = self.factory.get("/android/reportEventBusStop/v2/")
        request.user = AnonymousUser()

        request0 = self.factory.get("/android/requestEventsForBusStop/v2/")
        request0.user = AnonymousUser()

        reponse_view = RegisterEventBusStop()
        # make a report
        reponse_view.get(
            request,
            self.phone_id,
            stop_code,
            event_id,
            EventForBusStop.CONFIRM)

        # report one event, and confirm it
        response0_view = EventsByBusStop()
        response0 = response0_view.get(request0, stop_code)
        response0 = json.loads(response0.content)

        self.assertEqual(response0["codeBusStop"], stop_code)
        self.assertEqual(response0["events"][0]["eventDecline"], 0)
        self.assertEqual(response0["events"][0]["eventConfirm"], 1)
        self.assertEqual(response0["events"][0]["eventcode"], event_id)

        # do event +1 to the event
        reponse_view.get(
            request,
            self.phone_id,
            stop_code,
            event_id,
            EventForBusStop.CONFIRM)
        response0 = response0_view.get(request0, stop_code)
        response0 = json.loads(response0.content)

        self.assertEqual(response0["codeBusStop"], stop_code)
        self.assertEqual(response0["events"][0]["eventDecline"], 0)
        self.assertEqual(response0["events"][0]["eventConfirm"], 2)
        self.assertEqual(response0["events"][0]["eventcode"], event_id)

        # do event -1 to the event
        reponse_view.get(
            request,
            self.phone_id,
            stop_code,
            event_id,
            EventForBusStop.DECLINE)
        response0 = response0_view.get(request0, stop_code)
        response0 = json.loads(response0.content)

        self.assertEqual(response0["codeBusStop"], stop_code)
        self.assertEqual(response0["events"][0]["eventDecline"], 1)
        self.assertEqual(response0["events"][0]["eventConfirm"], 2)
        self.assertEqual(response0["events"][0]["eventcode"], event_id)

        # change manualy the timeStamp to simulate an event that has expired
        event_obj = Event.objects.get(id=event_id)
        event_for_stop_obj = EventForBusStop.objects.get(stopCode=stop_code, event=event_obj)

        time_delta = timezone.timedelta(minutes=event_obj.lifespam)
        event_for_stop_obj.expireTime = event_for_stop_obj.timeCreation - time_delta
        event_for_stop_obj.save()

        # ask for ecents and the answere should be none
        response0 = response0_view.get(request0, stop_code)
        response0 = json.loads(response0.content)

        self.assertEqual(len(response0["events"]), 0)

    def test_RequestUUIDBasedOnLicensePlate(self):
        """ test the method to request an uuid based on license plate """
        license_plates = ["AFJG21", "aFAf21", "AF-SD23", "FG-DF-45"]
        # it is a valid uuid
        pattern = re.compile(
            "^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")

        machine_id = None
        for licensePlate in license_plates:
            # machine id is a UUID
            machine_id = self.helper.askForMachineId(licensePlate)
            self.assertTrue((pattern.match(machine_id.upper()) if True else False))

        """ if request a second uuid with an old license plate, i must to get the same uuid """
        machine_id2 = self.helper.askForMachineId(license_plates[3])

        self.assertTrue(pattern.match(machine_id2.upper()))
        self.assertTrue(machine_id == machine_id2)

    def test_RequestUUIDBasedOnDummyLicensePlate(self):
        """ test the method to request an uuid based on dummy license plate """
        license_plate = Constants.DUMMY_LICENSE_PLATE

        uuid = self.helper.askForMachineId(license_plate)

        # it is a valid uuid
        pattern = re.compile(
            "^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")
        self.assertTrue((pattern.match(uuid.upper()) if True else False))

        """ if request a second uuid wiht dummy license plate, i must to get a new uuid """
        uuid2 = self.helper.askForMachineId(license_plate)

        self.assertTrue((pattern.match(uuid2.upper()) if True else False))
        self.assertFalse(uuid == uuid2)

    def test_MergeEventsFromTheSameBusButDifferenceService(self):
        """ test the method that merge event from the same bus machine but difference service """

        license_plate = "AA1111"
        route1 = "506"
        route2 = "509"
        event_code1 = "evn00230"
        event_code2 = "evn00240"
        event_code3 = "evn00232"

        # ask for bus and get the UUID
        test_uuid = self.helper.askForMachineId(license_plate)

        # create bus to create an assignment
        request = self.factory.get("/android/requestToken/v2/")
        request.user = AnonymousUser()
        reponse_view = RequestTokenV2()
        response = reponse_view.get(request, self.phone_id, route1, test_uuid)
        self.assertEqual(response.status_code, 200)

        # create bus to create an assignment
        request = self.factory.get("/android/requestToken/v2/")
        request.user = AnonymousUser()
        reponse_view = RequestTokenV2()
        response = reponse_view.get(request, self.phone_id, route2, test_uuid)
        self.assertEqual(response.status_code, 200)

        # submitting some events to the server
        request_to_report_event_bus = self.factory.get(
            "/android/reportEventBus/v2/")
        request_to_report_event_bus.user = AnonymousUser()

        # send first report with service 1
        report_event_bus_view = RegisterEventBusV2()
        response_to_report_event_bus = report_event_bus_view.get(request_to_report_event_bus,
                                                                 self.phone_id, test_uuid, route1, event_code1,
                                                                 EventForBusv2.CONFIRM)

        response_to_report_event_bus = json.loads(response_to_report_event_bus.content)

        self.assertEqual(response_to_report_event_bus["uuid"], test_uuid)
        self.assertEqual(
            response_to_report_event_bus["registrationPlate"],
            license_plate)
        self.assertEqual(response_to_report_event_bus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(response_to_report_event_bus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(response_to_report_event_bus["events"][
                             0]["eventcode"], event_code1)

        # send second report with service 2. We decline the previous event
        # reportd
        response_to_report_event_bus = report_event_bus_view.get(request_to_report_event_bus,
                                                                 self.phone_id, test_uuid, route2, event_code1,
                                                                 EventForBusv2.DECLINE)

        response_to_report_event_bus = json.loads(response_to_report_event_bus.content)

        self.assertEqual(response_to_report_event_bus["uuid"], test_uuid)
        self.assertEqual(
            response_to_report_event_bus["registrationPlate"],
            license_plate)
        self.assertEqual(response_to_report_event_bus[
                             "events"][0]["eventDecline"], 1)
        self.assertEqual(response_to_report_event_bus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(response_to_report_event_bus["events"][
                             0]["eventcode"], event_code1)

        # report second event to service
        response_to_report_event_bus = report_event_bus_view.get(request_to_report_event_bus,
                                                                 self.phone_id, test_uuid, route1, event_code2,
                                                                 EventForBusv2.CONFIRM)

        response_to_report_event_bus = json.loads(response_to_report_event_bus.content)

        self.assertEqual(response_to_report_event_bus["uuid"], test_uuid)
        self.assertEqual(response_to_report_event_bus["registrationPlate"], license_plate)
        self.assertEqual(response_to_report_event_bus["events"][0]["eventDecline"], 0)
        self.assertEqual(response_to_report_event_bus["events"][0]["eventConfirm"], 1)
        self.assertEqual(response_to_report_event_bus["events"][0]["eventcode"], event_code2)
        self.assertEqual(response_to_report_event_bus["events"][1]["eventDecline"], 1)
        self.assertEqual(response_to_report_event_bus["events"][1]["eventConfirm"], 1)
        self.assertEqual(response_to_report_event_bus["events"][1]["eventcode"], event_code1)

        # report third event to service
        response_to_report_event_bus = report_event_bus_view.get(request_to_report_event_bus,
                                                                 self.phone_id, test_uuid, route2, event_code3,
                                                                 EventForBusv2.CONFIRM)

        response_to_report_event_bus = json.loads(response_to_report_event_bus.content)

        self.assertEqual(response_to_report_event_bus["uuid"], test_uuid)
        self.assertEqual(
            response_to_report_event_bus["registrationPlate"],
            license_plate)
        self.assertEqual(response_to_report_event_bus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(response_to_report_event_bus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(response_to_report_event_bus["events"][
                             0]["eventcode"], event_code3)
        self.assertEqual(response_to_report_event_bus[
                             "events"][1]["eventDecline"], 0)
        self.assertEqual(response_to_report_event_bus[
                             "events"][1]["eventConfirm"], 1)
        self.assertEqual(response_to_report_event_bus["events"][
                             1]["eventcode"], event_code2)
        self.assertEqual(response_to_report_event_bus[
                             "events"][2]["eventDecline"], 1)
        self.assertEqual(response_to_report_event_bus[
                             "events"][2]["eventConfirm"], 1)
        self.assertEqual(response_to_report_event_bus["events"][
                             2]["eventcode"], event_code1)

    def test_AskForAnNonExistentBus(self):
        """ ask for events for a bus that does not exists """
        uuid = "2e5443b7-a824-4a78-bb62-6c4e24adaaeb"

        json_response = self.helper.requestEventsForBusV2(uuid)

        self.assertEqual(len(json_response["events"]), 0)
        self.assertEqual(json_response["registrationPlate"], "")
