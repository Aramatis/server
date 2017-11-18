import django
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.test import TransactionTestCase, RequestFactory
from django.utils import timezone

# views
import AndroidRequests.views as views
# my stuff
from AndroidRequests.models import DevicePositionInTime, ActiveToken, Token, EventForBusStop, Event, Busv2, \
    Busassignment
from gtfs.models import GTFS, BusStop, Service, ServiceStopDistance, ServiceLocation
from AndroidRequests.statusResponse import Status
from AndroidRequests.tests.testHelper import TestHelper


# Create your tests here.


class DevicePositionInTimeTestCase(TransactionTestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """

        minutes = timezone.timedelta(minutes=1)
        self.timeStamp = [timezone.now(), timezone.now() + minutes, timezone.now() + minutes + minutes]
        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.latitude = [-33.4577491104941, -
        33.4445256604888, -33.4402777996082]
        self.longitude = [-70.6634020999999, -70.6509264499999, -70.6433333]

    def test_consistency_model_DevicePositionInTime(self):
        """ This method test the database for the DevicePositionInTime model """

        for n in range(3):
            DevicePositionInTime.objects.create(phoneId=self.phoneId, longitude=self.longitude[n],
                                                latitude=self.latitude[n], timeStamp=self.timeStamp[n])

        for n in range(3):
            devicePosition = DevicePositionInTime.objects.get(
                longitude=self.longitude[n])
            self.assertEqual(devicePosition.latitude, self.latitude[n])
            self.assertEqual(devicePosition.timeStamp, self.timeStamp[n])

    def test_wrong_phoneId(self):
        """ create a register with a wrong phoneId """

        phoneId = "this is a wrong phoneId"

        if django.VERSION == (1, 8, 4, 'final', 0):
            self.assertRaises(ValueError,
                              DevicePositionInTime.objects.create,
                              phoneId=phoneId,
                              longitude=self.longitude[0],
                              latitude=self.latitude[0],
                              timeStamp=self.timeStamp[0])

        elif django.VERSION == (1, 11, 0, 'final', 0):
            self.assertRaises(ValidationError,
                              DevicePositionInTime.objects.create,
                              phoneId=phoneId,
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

        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        # inital config for DevicePositionInTime
        self.time = timezone.now()
        DevicePositionInTime.objects.create(
            phoneId=self.phoneId,
            longitude=3.5,
            latitude=5.2,
            timeStamp=self.time)
        DevicePositionInTime.objects.create(
            phoneId=self.phoneId,
            longitude=3.4,
            latitude=5.2,
            timeStamp=self.time)
        # this should not be answered
        DevicePositionInTime.objects.create(phoneId=self.phoneId, longitude=3.3, latitude=4.2, timeStamp=self.time
                                                                                                         - timezone.timedelta(
            minutes=11))

        # initial config for ActiveToken

        self.test = TestHelper(self)

        self.gtfs = GTFS.objects.get(version=settings.GTFS_VERSION)
        # add dummy  bus
        phoneId = '159fc6b77a20477eb5c7af421e1e0e16'
        registrationPlate = 'AA1111'
        service = '507'
        self.test.createBusAndAssignmentOnDatabase(phoneId=phoneId, service=service, licencePlate=registrationPlate)
        # add dummy bus stop
        busStop = BusStop.objects.create(
            code='PA459', gtfs=self.gtfs, name='bla', longitude=0, latitude=0)

        # add dummy service and its path
        # '#00a0f0'color_id = models.IntegerField(default = 0)
        Service.objects.create(
            service='507',
            gtfs=self.gtfs,
            origin='origin_test',
            destiny='destination_test')
        ServiceStopDistance.objects.create(
            busStop=busStop, gtfs=self.gtfs, service='507I', distance=5)
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

        longituds = [3.5, 3.4, 3.3]
        latituds = [5.2, 5.2, 4.2]
        timeStamps = [
            self.time,
            self.time,
            self.time -
            timezone.timedelta(
                minutes=11)]

        for cont in range(3):
            devicePosition = DevicePositionInTime.objects.get(
                longitude=longituds[cont])
            self.assertEqual(devicePosition.latitude, latituds[cont])
            self.assertEqual(devicePosition.timeStamp, timeStamps[cont])

    def test_consistencyModelActiveToken(self):
        """This method test the database for the ActiveToken model"""

        service = '503'
        licencePlate = 'ZZZZ00'
        travelToken = self.test.getInBusWithLicencePlateByPost(
            self.phoneId, service, licencePlate)

        # the created token is an active token
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=travelToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(
            Token.objects.filter(
                token=travelToken).exists(), True)

        jsonResponse = self.test.endRoute(travelToken)

        self.assertEqual(jsonResponse['response'], 'Trip ended.')

        # activeToken has to be missing but token has to exists
        self.assertEqual(
            ActiveToken.objects.filter(
                token__token=travelToken).exists(), False)
        self.assertEqual(
            Token.objects.filter(
                token=travelToken).exists(), True)

    def test_consistencyModelPoseInTrajectoryOfToken(self):
        """this method test the PoseInTrajectoryOfToken"""

        service = '503'
        licencePlate = 'ZZZZ00'
        testToken = self.test.getInBusWithLicencePlateByPost(
            self.phoneId, service, licencePlate)

        jsonResponse = self.test.sendFakeTrajectoryOfToken(testToken)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.OK, {})['message'])

        # remove the token
        self.test.endRoute(testToken)

        jsonResponse = self.test.sendFakeTrajectoryOfToken(testToken)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['message'])

    def test_EventsByBusStopReportNegativelyForFistTime(self):
        """ report stop event negatively for fist time """

        busStopCode = 'PA459'
        eventCode = 'evn00001'

        jsonResponse = self.test.confirmOrDeclineStopEvent(
            self.phoneId, busStopCode, eventCode, EventForBusStop.DECLINE)

        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

    def test_EventsByBusStop(self):
        """This method test two thing, the posibility to report an event and asking
        the events for the specific busStop"""

        busStopCode = 'PA459'
        eventCode = 'evn00001'
        # submitting some events to the server
        jsonResponse = self.test.reportStopEvent(
            self.phoneId, busStopCode, eventCode)

        # report one event, and confirm it
        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # do event +1 to the event
        jsonResponse = self.test.confirmOrDeclineStopEvent(
            self.phoneId, busStopCode, eventCode, EventForBusStop.CONFIRM)

        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # do event -1 to the event
        jsonResponse = self.test.confirmOrDeclineStopEvent(
            self.phoneId, busStopCode, eventCode, EventForBusStop.DECLINE)

        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # change manualy the timeStamp to simulate an event that has expired
        event = Event.objects.get(id=eventCode)
        stopEvent = EventForBusStop.objects.get(stopCode=busStopCode, event=event)
        timeDiff = timezone.timedelta(minutes=event.lifespam)
        stopEvent.expireTime = stopEvent.timeCreation - timeDiff
        stopEvent.save()

        # ask for ecents and the answere should be none
        jsonResponse = self.test.reportStopEvent(
            self.phoneId, busStopCode, eventCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

    def test_EventsByBusStopWithAditionalInfo(self):
        """This method test two thing, the posibility to report an event adding
        aditional information and asking the events for the specific busStop"""

        busStopCode = 'PA459'
        eventCode = 'evn00102'
        aditionalInfo = '507'
        # submitting some events to the server
        jsonResponse = self.test.reportStopEvent(
            self.phoneId, busStopCode, eventCode, aditionalInfo)
        # report one event, and confirm it
        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(len(jsonResponse['events']), 0)

        # event exists in database with aditional info saved
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusStop.objects.get(stopCode=busStopCode, event=event)

        self.assertEqual(anEvent.aditionalInfo, aditionalInfo)

    def test_EventsByBusStopWhereBusEventsAreAlwaysDifferentRecords(self):
        """This method test the posibility to report an event adding
        aditional information twice and should generate two records """

        busStopCode = 'PA459'

        eventCode1 = 'evn00102'
        aditionalInfo1 = '509'

        # submitting some events to the server
        jsonResponse = self.test.reportStopEvent(
            self.phoneId, busStopCode, eventCode1, aditionalInfo1)
        # report one event, and confirm it
        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(len(jsonResponse['events']), 0)

        # event exists in database with aditional info saved
        event = Event.objects.get(id=eventCode1)
        event = EventForBusStop.objects.get(stopCode=busStopCode, event=event)

        self.assertEqual(event.aditionalInfo, aditionalInfo1)

        eventCode2 = 'evn00102'
        aditionalInfo2 = '509'
        # submitting some events to the server
        jsonResponse = self.test.reportStopEvent(
            self.phoneId, busStopCode, eventCode2, aditionalInfo2)
        # report one event, and confirm it
        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(len(jsonResponse['events']), 0)

        # event exists in database with aditional info saved
        event = Event.objects.get(id=eventCode2)
        events = EventForBusStop.objects.filter(stopCode=busStopCode, event=event).order_by('timeCreation')

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].aditionalInfo, aditionalInfo1)
        self.assertEqual(events[1].aditionalInfo, aditionalInfo2)

    def test_registerPose(self):
        request = self.factory.get('/android/userPosition')
        request.user = AnonymousUser()
        lat = 45
        lon = 46
        response = views.userPosition(request, self.phoneId, lat, lon)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            DevicePositionInTime.objects.filter(
                longitude=lon,
                latitude=lat).exists(),
            True)

    def test_preferPositionOfPersonInsideABus(self):
        timeStampNow = str(timezone.localtime(timezone.now()))
        timeStampNow = timeStampNow[0:19]
        userLatitude = -33.458771
        userLongitude = -70.676266

        # first we test the position of the bus without passsangers
        thebus = Busv2.objects.create(registrationPlate='AA1112')
        busassignment = Busassignment.objects.create(service='507', uuid=thebus)

        busPose = busassignment.getLocation()

        self.assertTrue(busPose['random'])
        self.assertEqual(busPose['latitude'], -500)
        self.assertEqual(busPose['longitude'], -500)
        self.assertEqual(busPose['passengers'], 0)

        # add the position of a passanger inside the bus
        service = '507'
        licencePlate = 'AA1112'
        testToken = self.test.getInBusWithLicencePlateByPost(
            self.phoneId, service, licencePlate)

        testPoses = {"poses": [
            {"latitud": userLatitude, "longitud": userLongitude, "timeStamp": str(timeStampNow),
             "inVehicleOrNot": "vehicle"}]}

        jsonResponse = self.test.sendFakeTrajectoryOfToken(
            testToken, testPoses)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.OK, {})['message'])

        # ask the position of the bus whit a passanger
        bus = Busv2.objects.get(registrationPlate=licencePlate)
        busassignment = Busassignment.objects.get(uuid=bus, service=service)

        busPose = busassignment.getLocation()

        self.assertEqual(busPose['latitude'], userLatitude)
        self.assertEqual(busPose['longitude'], userLongitude)
        self.assertEqual(busPose['random'], False)
        self.assertEqual(busPose['passengers'] > 0, True)

        self.test.endRoute(testToken)
