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

        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.phoneId2 = "4f20c8f4-ddea-4c6c-87bb-c7bd3d435a51"

        # loads the events
        self.helper = TestHelper(self)

        # add dummy  bus
        self.licencePlate = "AA1111"
        self.service = "507"

        self.machineId = self.helper.askForMachineId(self.licencePlate)
        self.helper.getInBusWithMachineId(
            self.phoneId, self.service, self.machineId)

        # add dummy bus stop
        stopCode = "PA459"
        self.helper.insertBusstopsOnDatabase([stopCode])

        # add dummy service and its patha
        self.service = "507"
        self.direction = "I"
        self.helper.insertServicesOnDatabase([self.service])

        self.helper.insertServiceStopDistanceOnDatabase([stopCode])
        self.helper.insertServiceLocationOnDatabase([self.service + self.direction])

    def test_EventsByBusWithDummyLicensePlateUUID(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific dummy bus"""

        licencePlate = Constants.DUMMY_LICENSE_PLATE
        busService = "507"
        eventCode = "evn00202"

        machineId = self.helper.askForMachineId(licencePlate)

        # a ghost bus is created with the same uuid that was recieved
        self.assertEqual(Busv2.objects.filter(uuid=machineId).exists(), True)

        testToken = self.helper.getInBusWithMachineId(
            self.phoneId, busService, machineId)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)
        # the created token has the uuid for the dummybus
        # self.assertEqual(Token.objects.filter(uuid=puuid).exists(), True)

        # submitting one event to the server
        jsonResponse = self.helper.reportEventV2(
            self.phoneId, machineId, busService, eventCode)

        self.assertEqual(jsonResponse["uuid"], machineId)
        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 0)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 1)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        jsonResponse = self.helper.requestEventsForBusV2(machineId)

        # verify the previous event reported
        self.assertEqual(jsonResponse["uuid"], machineId)
        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 0)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 1)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        # ===================================================================================
        # do event +1 to the event
        jsonResponse = self.helper.confirmOrDeclineEventV2(self.phoneId, machineId, busService,
                                                           eventCode, EventForBusv2.CONFIRM)

        self.assertEqual(jsonResponse["uuid"], machineId)
        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 0)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 2)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        jsonResponse = self.helper.requestEventsForBusV2(machineId)

        # verify the previous event reported
        self.assertEqual(jsonResponse["uuid"], machineId)
        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 0)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 2)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        # do event -1 to the event
        jsonResponse = self.helper.confirmOrDeclineEventV2(self.phoneId, machineId, busService,
                                                           eventCode, EventForBusv2.DECLINE)

        self.assertEqual(jsonResponse["uuid"], machineId)
        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 1)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 2)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        jsonResponse = self.helper.requestEventsForBusV2(machineId)

        # verify the previous event reported
        self.assertEqual(jsonResponse["uuid"], machineId)
        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 1)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 2)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        # change manually the timeStamp to simulate an event that has expired
        bus = Busv2.objects.get(uuid=machineId)
        assignment = Busassignment.objects.get(service=busService, uuid=bus)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusv2.objects.get(
            busassignment=assignment, event=event)

        timeDelta = timezone.timedelta(minutes=event.lifespam)
        anEvent.expireTime = anEvent.timeCreation - timeDelta
        anEvent.save()

        # ask for events and the answer should be none
        jsonResponse = self.helper.requestEventsForBusV2(machineId)

        self.assertEqual(len(jsonResponse["events"]), 0)

    def test_EventsByBusv2(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific bus"""

        licencePlate = "AA1111"
        busService = "507"
        eventCode = "evn00202"

        machineId = self.helper.askForMachineId(licencePlate)

        # submitting one event to the server
        jsonResponse = self.helper.reportEventV2(
            self.phoneId, machineId, busService, eventCode)

        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 0)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 1)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        requestToRequestEventForBus = self.factory.get(
            "/android/requestEventsForBus/v2/")
        requestToRequestEventForBus.user = AnonymousUser()

        # verify the previous event reported
        requestEventForBusView = EventsByBusV2()
        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,
                                                                  machineId)

        responseToRequestEventForBus = json.loads(
            responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus[
                             "registrationPlate"], licencePlate)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventcode"], eventCode)

        # ===================================================================================
        # do event +1 to the event
        jsonResponse = self.helper.confirmOrDeclineEventV2(
            self.phoneId, machineId, busService, eventCode, EventForBusv2.CONFIRM)

        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 0)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 2)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,
                                                                  machineId)
        responseToRequestEventForBus = json.loads(
            responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus[
                             "registrationPlate"], licencePlate)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventConfirm"], 2)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventcode"], eventCode)

        # do event -1 to the event
        jsonResponse = self.helper.confirmOrDeclineEventV2(
            self.phoneId, machineId, busService, eventCode, EventForBusStop.DECLINE)

        self.assertEqual(jsonResponse["registrationPlate"], licencePlate)
        self.assertEqual(jsonResponse["events"][0]["eventDecline"], 1)
        self.assertEqual(jsonResponse["events"][0]["eventConfirm"], 2)
        self.assertEqual(jsonResponse["events"][0]["eventcode"], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,
                                                                  machineId)
        responseToRequestEventForBus = json.loads(
            responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus[
                             "registrationPlate"], licencePlate)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventDecline"], 1)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventConfirm"], 2)
        self.assertEqual(responseToRequestEventForBus[
                             "events"][0]["eventcode"], eventCode)

        # change manually the timeStamp to simulate an event that has expired
        # bus= Bus.objects.get(registrationPlate=licencePlate, service=route)
        bus = Busv2.objects.get(registrationPlate=licencePlate)
        busassignment = Busassignment.objects.get(uuid=bus, service=busService)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusv2.objects.get(
            busassignment=busassignment, event=event)

        timeDelta = timezone.timedelta(minutes=event.lifespam)
        anEvent.expireTime = anEvent.timeCreation - timeDelta
        anEvent.save()

        # ask for events and the answer should be none
        responseToRequestEventForBus = requestEventForBusView.get(
            requestToRequestEventForBus, bus.uuid)
        responseToRequestEventForBus = json.loads(
            responseToRequestEventForBus.content)

        self.assertEqual(len(responseToRequestEventForBus["events"]), 0)

    def test_EventsByBusStopv2(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific busStop"""

        busStopCode = "PA459"
        eventCode = "evn00001"
        # submitting some events to the server
        request = self.factory.get("/android/reportEventBusStop/v2/")
        request.user = AnonymousUser()

        request0 = self.factory.get("/android/requestEventsForBusStop/v2/")
        request0.user = AnonymousUser()

        reponseView = RegisterEventBusStop()
        # make a report
        reponseView.get(
            request,
            self.phoneId,
            busStopCode,
            eventCode,
            EventForBusStop.CONFIRM)

        # report one event, and confirm it
        response0View = EventsByBusStop()
        response0 = response0View.get(request0, busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0["codeBusStop"], busStopCode)
        self.assertEqual(response0["events"][0]["eventDecline"], 0)
        self.assertEqual(response0["events"][0]["eventConfirm"], 1)
        self.assertEqual(response0["events"][0]["eventcode"], eventCode)

        # do event +1 to the event
        reponseView.get(
            request,
            self.phoneId,
            busStopCode,
            eventCode,
            EventForBusStop.CONFIRM)
        response0 = response0View.get(request0, busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0["codeBusStop"], busStopCode)
        self.assertEqual(response0["events"][0]["eventDecline"], 0)
        self.assertEqual(response0["events"][0]["eventConfirm"], 2)
        self.assertEqual(response0["events"][0]["eventcode"], eventCode)

        # do event -1 to the event
        reponseView.get(
            request,
            self.phoneId,
            busStopCode,
            eventCode,
            EventForBusStop.DECLINE)
        response0 = response0View.get(request0, busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0["codeBusStop"], busStopCode)
        self.assertEqual(response0["events"][0]["eventDecline"], 1)
        self.assertEqual(response0["events"][0]["eventConfirm"], 2)
        self.assertEqual(response0["events"][0]["eventcode"], eventCode)

        # change manualy the timeStamp to simulate an event that has expired
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusStop.objects.get(stopCode=busStopCode, event=event)

        timeDelta = timezone.timedelta(minutes=event.lifespam)
        anEvent.expireTime = anEvent.timeCreation - timeDelta
        anEvent.save()

        # ask for ecents and the answere should be none
        response0 = response0View.get(request0, busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(len(response0["events"]), 0)

    def test_RequestUUIDBasedOnLicensePlate(self):
        """ test the method to request an uuid based on license plate """
        licensePlates = ["AFJG21", "aFAf21", "AF-SD23", "FG-DF-45"]
        # it is a valid uuid
        pattern = re.compile(
            "^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")

        machine_id = None
        for licensePlate in licensePlates:
            # machine id is a UUID
            machine_id = self.helper.askForMachineId(licensePlate)
            self.assertTrue((pattern.match(machine_id.upper()) if True else False))

        """ if request a second uuid with an old license plate, i must to get the same uuid """
        machine_id2 = self.helper.askForMachineId(licensePlates[3])

        self.assertTrue(pattern.match(machine_id2.upper()))
        self.assertTrue(machine_id == machine_id2)

    def test_RequestUUIDBasedOnDummyLicensePlate(self):
        """ test the method to request an uuid based on dummy license plate """
        licensePlate = Constants.DUMMY_LICENSE_PLATE

        uuid = self.helper.askForMachineId(licensePlate)

        # it is a valid uuid
        pattern = re.compile(
            "^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")
        self.assertTrue((pattern.match(uuid.upper()) if True else False))

        """ if request a second uuid wiht dummy license plate, i must to get a new uuid """
        uuid2 = self.helper.askForMachineId(licensePlate)

        self.assertTrue((pattern.match(uuid2.upper()) if True else False))
        self.assertFalse(uuid == uuid2)

    def test_MergeEventsFromTheSameBusButDifferenceService(self):
        """ test the method that merge event from the same bus machine but difference service """

        licensePlate = "AA1111"
        busService1 = "506"
        busService2 = "509"
        eventCode1 = "evn00230"
        eventCode2 = "evn00240"
        eventCode3 = "evn00232"

        # ask for bus and get the UUID
        testUUID = self.helper.askForMachineId(licensePlate)

        # create bus to create an assignment
        request = self.factory.get("/android/requestToken/v2/")
        request.user = AnonymousUser()
        reponseView = RequestTokenV2()
        response = reponseView.get(request, self.phoneId, busService1, testUUID)
        self.assertEqual(response.status_code, 200)

        # create bus to create an assignment
        request = self.factory.get("/android/requestToken/v2/")
        request.user = AnonymousUser()
        reponseView = RequestTokenV2()
        response = reponseView.get(request, self.phoneId, busService2, testUUID)
        self.assertEqual(response.status_code, 200)

        # submitting some events to the server
        requestToReportEventBus = self.factory.get(
            "/android/reportEventBus/v2/")
        requestToReportEventBus.user = AnonymousUser()

        # send first report with service 1
        reportEventBusView = RegisterEventBusV2()
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus,
                                                          self.phoneId, testUUID, busService1, eventCode1,
                                                          EventForBusv2.CONFIRM)

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus["uuid"], testUUID)
        self.assertEqual(
            responseToReportEventBus["registrationPlate"],
            licensePlate)
        self.assertEqual(responseToReportEventBus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(responseToReportEventBus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(responseToReportEventBus["events"][
                             0]["eventcode"], eventCode1)

        # send second report with service 2. We decline the previous event
        # reportd
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus,
                                                          self.phoneId, testUUID, busService2, eventCode1,
                                                          EventForBusv2.DECLINE)

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus["uuid"], testUUID)
        self.assertEqual(
            responseToReportEventBus["registrationPlate"],
            licensePlate)
        self.assertEqual(responseToReportEventBus[
                             "events"][0]["eventDecline"], 1)
        self.assertEqual(responseToReportEventBus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(responseToReportEventBus["events"][
                             0]["eventcode"], eventCode1)

        # report second event to service
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus,
                                                          self.phoneId, testUUID, busService1, eventCode2,
                                                          EventForBusv2.CONFIRM)

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus["uuid"], testUUID)
        self.assertEqual(responseToReportEventBus["registrationPlate"], licensePlate)
        self.assertEqual(responseToReportEventBus["events"][0]["eventDecline"], 0)
        self.assertEqual(responseToReportEventBus["events"][0]["eventConfirm"], 1)
        self.assertEqual(responseToReportEventBus["events"][0]["eventcode"], eventCode2)
        self.assertEqual(responseToReportEventBus["events"][1]["eventDecline"], 1)
        self.assertEqual(responseToReportEventBus["events"][1]["eventConfirm"], 1)
        self.assertEqual(responseToReportEventBus["events"][1]["eventcode"], eventCode1)

        # report third event to service
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus,
                                                          self.phoneId, testUUID, busService2, eventCode3,
                                                          EventForBusv2.CONFIRM)

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus["uuid"], testUUID)
        self.assertEqual(
            responseToReportEventBus["registrationPlate"],
            licensePlate)
        self.assertEqual(responseToReportEventBus[
                             "events"][0]["eventDecline"], 0)
        self.assertEqual(responseToReportEventBus[
                             "events"][0]["eventConfirm"], 1)
        self.assertEqual(responseToReportEventBus["events"][
                             0]["eventcode"], eventCode3)
        self.assertEqual(responseToReportEventBus[
                             "events"][1]["eventDecline"], 0)
        self.assertEqual(responseToReportEventBus[
                             "events"][1]["eventConfirm"], 1)
        self.assertEqual(responseToReportEventBus["events"][
                             1]["eventcode"], eventCode2)
        self.assertEqual(responseToReportEventBus[
                             "events"][2]["eventDecline"], 1)
        self.assertEqual(responseToReportEventBus[
                             "events"][2]["eventConfirm"], 1)
        self.assertEqual(responseToReportEventBus["events"][
                             2]["eventcode"], eventCode1)

    def test_AskForAnNonExistentBus(self):
        """ ask for events for a bus that does not exists """
        uuid = "2e5443b7-a824-4a78-bb62-6c4e24adaaeb"

        jsonResponse = self.helper.requestEventsForBusV2(uuid)

        self.assertEqual(len(jsonResponse["events"]), 0)
        self.assertEqual(jsonResponse["registrationPlate"], "")
