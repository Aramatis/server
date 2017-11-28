from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.test import TransactionTestCase, RequestFactory
from django.utils import timezone

from AndroidRequests.models import DevicePositionInTime, ActiveToken, Token, EventForBusStop, Event, Busv2, \
    Busassignment
from gtfs.models import GTFS, BusStop, Service, ServiceStopDistance, ServiceLocation
from AndroidRequests.statusResponse import Status
from AndroidRequests.tests.testHelper import TestHelper

import AndroidRequests.views as views
import django


class DevicePositionInTimeTestCase(TransactionTestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """

        minutes = timezone.timedelta(minutes=1)
        self.timeStamp = [timezone.now(), timezone.now() + minutes, timezone.now() + minutes + minutes]
        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.latitude = [-33.4577491104941, -33.4445256604888, -33.4402777996082]
        self.longitude = [-70.6634020999999, -70.6509264499999, -70.6433333]

    def test_consistency_model_DevicePositionInTime(self):
        """ This method test the database for the DevicePositionInTime model """

        for n in range(3):
            DevicePositionInTime.objects.create(phoneId=self.phone_id, longitude=self.longitude[n],
                                                latitude=self.latitude[n], timeStamp=self.timeStamp[n])

        for n in range(3):
            device_position = DevicePositionInTime.objects.get(
                longitude=self.longitude[n])
            self.assertEqual(device_position.latitude, self.latitude[n])
            self.assertEqual(device_position.timeStamp, self.timeStamp[n])

    def test_wrong_phoneId(self):
        """ create a register with a wrong phoneId """

        phone_id = "this is a wrong phoneId"

        if django.VERSION == (1, 8, 4, 'final', 0):
            self.assertRaises(ValueError,
                              DevicePositionInTime.objects.create,
                              phoneId=phone_id,
                              longitude=self.longitude[0],
                              latitude=self.latitude[0],
                              timeStamp=self.timeStamp[0])

        elif django.VERSION == (1, 11, 0, 'final', 0):
            self.assertRaises(ValidationError,
                              DevicePositionInTime.objects.create,
                              phoneId=phone_id,
                              longitude=self.longitude[0],
                              latitude=self.latitude[0],
                              timeStamp=self.timeStamp[0])


class DevicePositionInTimeTest(TransactionTestCase):
    """ test for DevicePositionInTime model """
    fixtures = ["events"]

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        # inital config for DevicePositionInTime
        self.time = timezone.now()
        DevicePositionInTime.objects.create(
            phoneId=self.phone_id,
            longitude=3.5,
            latitude=5.2,
            timeStamp=self.time)
        DevicePositionInTime.objects.create(
            phoneId=self.phone_id,
            longitude=3.4,
            latitude=5.2,
            timeStamp=self.time)
        # this should not be answered
        DevicePositionInTime.objects.create(phoneId=self.phone_id, longitude=3.3, latitude=4.2,
                                            timeStamp=self.time - timezone.timedelta(minutes=11))

        self.test = TestHelper(self)

        self.gtfs = GTFS.objects.create(version=settings.GTFS_VERSION, timeCreation=timezone.now())

        # add dummy  bus
        phone_id = '159fc6b77a20477eb5c7af421e1e0e16'
        license_plate = 'AA1111'
        route = '507'
        self.test.createBusAndAssignmentOnDatabase(phone_id=phone_id, route=route, license_plate=license_plate)
        # add dummy bus stop
        stop_obj = BusStop.objects.create(
            code='PA459', gtfs=self.gtfs, name='bla', longitude=0, latitude=0)

        # add dummy service and its path
        # '#00a0f0'color_id = models.IntegerField(default = 0)
        Service.objects.create(
            service='507',
            gtfs=self.gtfs,
            origin='origin_test',
            destiny='destination_test')
        ServiceStopDistance.objects.create(
            busStop=stop_obj, gtfs=self.gtfs, service='507I', distance=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=1, longitude=4, latitude=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=2, longitude=5, latitude=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=3, longitude=6, latitude=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=4, longitude=7, latitude=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=5, longitude=8, latitude=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=6, longitude=9, latitude=5)

    def test_consistencyModelDevicePositionInTime(self):
        """This method test the database for the DevicePositionInTime model"""

        longitudes = [3.5, 3.4, 3.3]
        latitudes = [5.2, 5.2, 4.2]
        timestamps = [
            self.time,
            self.time,
            self.time -
            timezone.timedelta(
                minutes=11)]

        for cont in range(3):
            device_position = DevicePositionInTime.objects.get(
                longitude=longitudes[cont])
            self.assertEqual(device_position.latitude, latitudes[cont])
            self.assertEqual(device_position.timeStamp, timestamps[cont])

    def test_consistencyModelActiveToken(self):
        """This method test the database for the ActiveToken model"""

        route = '503'
        license_plate = 'ZZZZ00'
        travel_token = self.test.getInBusWithLicencePlateByPost(
            self.phone_id, route, license_plate)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=travel_token).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(
            Token.objects.filter(
                token=travel_token).exists(), True)

        json_response = self.test.endRoute(travel_token)

        self.assertEqual(json_response['response'], 'Trip ended.')

        # activeToken has to be missing but token has to exists
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=travel_token).exists(), False)
        self.assertEqual(
            Token.objects.filter(
                token=travel_token).exists(), True)

    def test_consistencyModelPoseInTrajectoryOfToken(self):
        """this method test the PoseInTrajectoryOfToken"""

        route = '503'
        license_plate = 'ZZZZ00'
        test_token = self.test.getInBusWithLicencePlateByPost(
            self.phone_id, route, license_plate)

        json_response = self.test.sendFakeTrajectoryOfToken(test_token)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_response['message'], Status.getJsonStatus(Status.OK, {})['message'])

        # remove the token
        self.test.endRoute(test_token)

        json_response = self.test.sendFakeTrajectoryOfToken(test_token)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['status'])
        self.assertEqual(json_response['message'],
                         Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['message'])

    def test_EventsByBusStopReportNegativelyForFistTime(self):
        """ report stop event negatively for fist time """

        stop_code = 'PA459'
        event_id = 'evn00001'

        json_response = self.test.confirmOrDeclineStopEvent(self.phone_id, stop_code, event_id, EventForBusStop.DECLINE)

        self.assertEqual(json_response['codeBusStop'], stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 1)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 0)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

    def test_EventsByBusStop(self):
        """This method test two thing, the possibility to report an event and asking
        the events for the specific busStop"""

        stop_code = 'PA459'
        event_id = 'evn00001'
        # submitting some events to the server
        json_response = self.test.reportStopEvent(self.phone_id, stop_code, event_id)

        # report one event, and confirm it
        self.assertEqual(json_response['codeBusStop'], stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

        # do event +1 to the event
        json_response = self.test.confirmOrDeclineStopEvent(
            self.phone_id, stop_code, event_id, EventForBusStop.CONFIRM)

        self.assertEqual(json_response['codeBusStop'], stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 2)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

        # do event -1 to the event
        json_response = self.test.confirmOrDeclineStopEvent(
            self.phone_id, stop_code, event_id, EventForBusStop.DECLINE)

        self.assertEqual(json_response['codeBusStop'], stop_code)
        self.assertEqual(json_response['events'][0]['eventDecline'], 1)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 2)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

        # change manualy the timeStamp to simulate an event that has expired
        event_obj = Event.objects.get(id=event_id)
        stop_event = EventForBusStop.objects.get(stopCode=stop_code, event=event_obj)
        time_diff = timezone.timedelta(minutes=event_obj.lifespam)
        stop_event.expireTime = stop_event.timeCreation - time_diff
        stop_event.save()

        # ask for ecents and the answere should be none
        json_response = self.test.reportStopEvent(self.phone_id, stop_code, event_id)
        self.assertEqual(json_response['events'][0]['eventDecline'], 0)
        self.assertEqual(json_response['events'][0]['eventConfirm'], 1)
        self.assertEqual(json_response['events'][0]['eventcode'], event_id)

    def test_EventsByBusStopWithAditionalInfo(self):
        """This method test two thing, the posibility to report an event adding
        additional information and asking the events for the specific busStop"""

        stop_code = 'PA459'
        event_id = 'evn00102'
        additional_info = '507'
        # submitting some events to the server
        json_response = self.test.reportStopEvent(self.phone_id, stop_code, event_id, additional_info)
        # report one event, and confirm it
        self.assertEqual(json_response['codeBusStop'], stop_code)
        self.assertEqual(len(json_response['events']), 0)

        # event exists in database with aditional info saved
        event_obj = Event.objects.get(id=event_id)
        event_for_stop_obj = EventForBusStop.objects.get(stopCode=stop_code, event=event_obj)

        self.assertEqual(event_for_stop_obj.aditionalInfo, additional_info)

    def test_EventsByBusStopWhereBusEventsAreAlwaysDifferentRecords(self):
        """This method test the posibility to report an event adding
        additional information twice and should generate two records """

        stop_code = 'PA459'

        event_id = 'evn00102'
        additional_info1 = '509'

        # submitting some events to the server
        json_response = self.test.reportStopEvent(self.phone_id, stop_code, event_id, additional_info1)
        # report one event, and confirm it
        self.assertEqual(json_response['codeBusStop'], stop_code)
        self.assertEqual(len(json_response['events']), 0)

        # event exists in database with additional info saved
        event_obj = Event.objects.get(id=event_id)
        event_obj = EventForBusStop.objects.get(stopCode=stop_code, event=event_obj)

        self.assertEqual(event_obj.aditionalInfo, additional_info1)

        event_id2 = 'evn00102'
        additional_info2 = '509'
        # submitting some events to the server
        json_response = self.test.reportStopEvent(self.phone_id, stop_code, event_id2, additional_info2)
        # report one event, and confirm it
        self.assertEqual(json_response['codeBusStop'], stop_code)
        self.assertEqual(len(json_response['events']), 0)

        # event exists in database with aditional info saved
        event_obj = Event.objects.get(id=event_id2)
        events = EventForBusStop.objects.filter(stopCode=stop_code, event=event_obj).order_by('timeCreation')

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].aditionalInfo, additional_info1)
        self.assertEqual(events[1].aditionalInfo, additional_info2)

    def test_registerPose(self):
        request = self.factory.get('/android/userPosition')
        request.user = AnonymousUser()
        lat = 45
        lon = 46
        response = views.save_user_position(request, self.phone_id, lat, lon)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            DevicePositionInTime.objects.filter(
                longitude=lon,
                latitude=lat).exists(),
            True)

    def test_preferPositionOfPersonInsideABus(self):
        timestamp_now = str(timezone.localtime(timezone.now()))
        timestamp_now = timestamp_now[0:19]
        user_latitude = -33.458771
        user_longitude = -70.676266

        # first we test the position of the bus without passsangers
        bus_obj = Busv2.objects.create(registrationPlate='AA1112')
        bus_assignment_obj = Busassignment.objects.create(service='507', uuid=bus_obj)

        bus_location = bus_assignment_obj.get_location()

        self.assertTrue(bus_location['random'])
        self.assertEqual(bus_location['latitude'], -500)
        self.assertEqual(bus_location['longitude'], -500)
        self.assertEqual(bus_location['passengers'], 0)

        # add the position of a passanger inside the bus
        route = '507'
        license_plate = 'AA1112'
        test_token = self.test.getInBusWithLicencePlateByPost(self.phone_id, route, license_plate)

        test_locations = {"poses": [
            {"latitud": user_latitude, "longitud": user_longitude, "timeStamp": str(timestamp_now),
             "inVehicleOrNot": "vehicle"}]}

        json_response = self.test.sendFakeTrajectoryOfToken(
            test_token, test_locations)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_response['message'], Status.getJsonStatus(Status.OK, {})['message'])

        # ask the position of the bus whit a passanger
        bus = Busv2.objects.get(registrationPlate=license_plate)
        bus_assignment_obj = Busassignment.objects.get(uuid=bus, service=route)

        bus_location = bus_assignment_obj.get_location()

        self.assertEqual(bus_location['latitude'], user_latitude)
        self.assertEqual(bus_location['longitude'], user_longitude)
        self.assertEqual(bus_location['random'], False)
        self.assertEqual(bus_location['passengers'] > 0, True)

        self.test.endRoute(test_token)
