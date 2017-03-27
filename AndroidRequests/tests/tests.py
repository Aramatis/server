from django.test import TransactionTestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

# my stuff
from AndroidRequests.models import DevicePositionInTime, BusStop, Service, ServiceStopDistance, ServiceLocation, ActiveToken, Token, EventForBusStop, Event, Busv2, Busassignment, GTFS
# views
import AndroidRequests.views as views
from AndroidRequests.tests.testHelper import TestHelper

# Create your tests here.


class DevicePositionInTimeTestCase(TransactionTestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.timeStamp = [timezone.now(), timezone.now(), timezone.now()]
        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.latitude = [-33.4577491104941, -
                         33.4445256604888, -33.4402777996082]
        self.longitude = [-70.6634020999999, -70.6509264499999, -70.6433333]

    def test_consistency_model_DevicePositionInTime(self):
        """ This method test the database for the DevicePositionInTime model """

        for n in range(3):
            DevicePositionInTime.objects.create(userId=self.userId, longitud=self.longitude[n],
                                                latitud=self.latitude[n], timeStamp=self.timeStamp[n])

        for n in range(3):
            devicePosition = DevicePositionInTime.objects.get(
                longitud=self.longitude[n])
            self.assertEqual(devicePosition.latitud, self.latitude[n])
            self.assertEqual(devicePosition.timeStamp, self.timeStamp[n])

    def test_wrong_userId(self):
        """ create a register with a wrong userId """

        userId = "this is a wrong userid"

        self.assertRaises(ValueError,
                          DevicePositionInTime.objects.create,
                          userId=userId,
                          longitud=self.latitude[0],
                          latitud=self.longitude[0],
                          timeStamp=self.timeStamp[0])
        # "badly formed hexadecimal UUID string")


class DevicePositionInTimeTest(TransactionTestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        # inital config for DevicePositionInTime
        self.time = timezone.now()
        DevicePositionInTime.objects.create(
            userId=self.userId,
            longitud=3.5,
            latitud=5.2,
            timeStamp=self.time)
        DevicePositionInTime.objects.create(
            userId=self.userId,
            longitud=3.4,
            latitud=5.2,
            timeStamp=self.time)
        # this should not be answered
        DevicePositionInTime.objects.create(userId=self.userId, longitud=3.3, latitud=4.2, timeStamp=self.time
                                            - timezone.timedelta(minutes=11))

        # initial config for ActiveToken

        self.test = TestHelper(self)

        self.test.insertEventsOnDatabase()

        self.gtfs = GTFS.objects.get(version=settings.GTFS_VERSION)
        # add dummy  bus
        userId = '159fc6b77a20477eb5c7af421e1e0e16'
        registrationPlate = 'AA1111'
        service = '507'
        self.test.createBusAndAssignmentOnDatabase(userId=userId, service=service, licencePlate=registrationPlate)
        # add dummy bus stop
        busStop = BusStop.objects.create(
            code='PA459', gtfs=self.gtfs, name='bla', longitud=0, latitud=0)

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
            service='507I', gtfs=self.gtfs, distance=1, longitud=4, latitud=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=2, longitud=5, latitud=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=3, longitud=6, latitud=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=4, longitud=7, latitud=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=5, longitud=8, latitud=5)
        ServiceLocation.objects.create(
            service='507I', gtfs=self.gtfs, distance=6, longitud=9, latitud=5)

    def test_consistencyModelDevicePositionInTime(self):
        '''This method test the database for the DevicePositionInTime model'''

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
                longitud=longituds[cont])
            self.assertEqual(devicePosition.latitud, latituds[cont])
            self.assertEqual(devicePosition.timeStamp, timeStamps[cont])

    def test_consistencyModelActiveToken(self):
        '''This method test the database for the ActiveToken model'''

        service = '503'
        licencePlate = 'ZZZZ00'
        travelToken = self.test.getInBusWithLicencePlate(
            self.userId, service, licencePlate)

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
        '''this method test the PoseInTrajectoryOfToken'''

        service = '503'
        licencePlate = 'ZZZZ00'
        testToken = self.test.getInBusWithLicencePlate(
            self.userId, service, licencePlate)

        jsonResponse = self.test.sendFakeTrajectoryOfToken(testToken)

        self.assertEqual(jsonResponse['response'], 'Poses were register.')

        # remove the token
        self.test.endRoute(testToken)

        jsonResponse = self.test.sendFakeTrajectoryOfToken(testToken)

        self.assertEqual(jsonResponse['response'], 'Token doesn\'t exist.')

    def test_EventsByBusStopReportNegativelyForFistTime(self):
        """ report stop event negatively for fist time """

        busStopCode = 'PA459'
        eventCode = 'evn00001'

        jsonResponse = self.test.confirmOrDeclineStopEvent(
            self.userId, busStopCode, eventCode, 'decline')

        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

    def test_EventsByBusStop(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific busStop'''

        busStopCode = 'PA459'
        eventCode = 'evn00001'
        # submitting some events to the server
        jsonResponse = self.test.reportStopEvent(
            self.userId, busStopCode, eventCode)

        # report one event, and confirm it
        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # do event +1 to the event
        jsonResponse = self.test.confirmOrDeclineStopEvent(
            self.userId, busStopCode, eventCode, 'confirm')

        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # do event -1 to the event
        jsonResponse = self.test.confirmOrDeclineStopEvent(
            self.userId, busStopCode, eventCode, 'decline')

        self.assertEqual(jsonResponse['codeBusStop'], busStopCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # change manualy the timeStamp to simulate an event that has expired
        busStop = BusStop.objects.get(code=busStopCode, gtfs__version=settings.GTFS_VERSION)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusStop.objects.get(busStop=busStop, event=event)

        anEvent.timeStamp = anEvent.timeCreation - \
            timezone.timedelta(minutes=event.lifespam)
        anEvent.save()

        # ask for ecents and the answere should be none
        jsonResponse = self.test.reportStopEvent(
            self.userId, busStopCode, eventCode)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

    def test_registerPose(self):
        request = self.factory.get('/android/userPosition')
        request.user = AnonymousUser()
        lat = 45
        lon = 46
        response = views.userPosition(request, self.userId, lat, lon)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            DevicePositionInTime.objects.filter(
                longitud=lon,
                latitud=lat).exists(),
            True)

    def test_preferPositionOfPersonInsideABus(self):

        timeStampNow = str(timezone.localtime(timezone.now()))
        timeStampNow = timeStampNow[0:19]
        userLatitud = -33.458771
        userLongitud = -70.676266

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
        testToken = self.test.getInBusWithLicencePlate(
            self.userId, service, licencePlate)

        testPoses = {"poses": [
            {"latitud": userLatitud, "longitud": userLongitud, "timeStamp": str(timeStampNow), "inVehicleOrNot": "vehicle"}]}

        jsonResponse = self.test.sendFakeTrajectoryOfToken(
            testToken, testPoses)

        self.assertEqual(jsonResponse['response'], 'Poses were register.')

        # ask the position of the bus whit a passanger
        bus = Busv2.objects.get(registrationPlate=licencePlate)
        busassignment = Busassignment.objects.get(uuid=bus, service=service)

        busPose = busassignment.getLocation()

        self.assertEqual(busPose['latitude'], userLatitud)
        self.assertEqual(busPose['longitude'], userLongitud)
        self.assertEqual(busPose['random'], False)
        self.assertEqual(busPose['passengers'] > 0, True)

        self.test.endRoute(testToken)
