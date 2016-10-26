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

# Create your tests here.

class DevicePositionInTimeTestCase(TestCase):
    """ test for DevicePositionInTime model """
    def setUp(self):
        """ this method will automatically call for every single test """

        self.timeStamp = [timezone.now(), timezone.now(), timezone.now()]
        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.latitude = [-33.4577491104941, -33.4445256604888, -33.4402777996082]
        self.longitude = [-70.6634020999999, -70.6509264499999, -70.6433333]

    def test_consistency_model_DevicePositionInTime(self):
        """ This method test the database for the DevicePositionInTime model """

        for n in range(3):
            DevicePositionInTime.objects.create(userId = self.userId, longitud = self.longitude[n],\
                    latitud = self.latitude[n], timeStamp = self.timeStamp[n])

        for n in range(3):
            devicePosition = DevicePositionInTime.objects.get(longitud = self.longitude[n])
            self.assertEqual(devicePosition.latitud, self.latitude[n])
            self.assertEqual(devicePosition.timeStamp, self.timeStamp[n])

    def test_wrong_userId(self):
        """ create a register with a wrong userId """

        userId = "this is a wrong userid"

        self.assertRaises(ValueError,\
                DevicePositionInTime.objects.create,\
                userId = userId,\
                longitud = self.latitude[0],\
                latitud = self.longitude[0],\
                timeStamp = self.timeStamp[0])
                #"badly formed hexadecimal UUID string")

class DevicePositionInTimeTest(TestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        # inital config for DevicePositionInTime
        self.time = timezone.now()
        DevicePositionInTime.objects.create(userId = self.userId, longitud = 3.5, latitud = 5.2, timeStamp = self.time)
        DevicePositionInTime.objects.create(userId = self.userId, longitud = 3.4, latitud = 5.2, timeStamp = self.time)
        # this should not be answered
        DevicePositionInTime.objects.create(userId = self.userId, longitud = 3.3, latitud = 4.2, timeStamp = self.time\
                -timezone.timedelta(minutes=11))

        # initial config for ActiveToken

        #loads the events
        import os, sys
        from Loaders.LoaderFactory import LoaderFactory

        log = open('loadDataErrorTest.log', 'w')

        csv = open('InitialData/events.csv', 'r') #path to Bus Stop csv file
        csv.next()
        factory = LoaderFactory()
        loader = factory.getModelLoader('event')(csv, log)
        loader.load()
        csv.close()
        log.close()

        # add dummy  bus
        Bus.objects.create(registrationPlate = 'AA1111', service = '507', uuid = '159fc6b7-7a20-477e-b5c7-af421e1e0e16')
        # add dummy bus stop
        busStop = BusStop.objects.create(code='PA459', name='bla',longitud=0,latitud=0)

        # add dummy service and its path
        Service.objects.create( service = '507', origin = 'origin_test', destiny = 'destination_test')#'#00a0f0'color_id = models.IntegerField(default = 0)
        ServiceStopDistance.objects.create( busStop = busStop,  service = '507I', distance = 5)
        ServiceLocation.objects.create(service = '507I', distance = 1, longitud=4, latitud=5)
        ServiceLocation.objects.create(service = '507I', distance = 2, longitud=5, latitud=5)
        ServiceLocation.objects.create(service = '507I', distance = 3, longitud=6, latitud=5)
        ServiceLocation.objects.create(service = '507I', distance = 4, longitud=7, latitud=5)
        ServiceLocation.objects.create(service = '507I', distance = 5, longitud=8, latitud=5)
        ServiceLocation.objects.create(service = '507I', distance = 6, longitud=9, latitud=5)

    def test_consistencyModelDevicePositionInTime(self):
        '''This method test the database for the DevicePositionInTime model'''

        longituds = [3.5, 3.4, 3.3]
        latituds = [5.2, 5.2, 4.2]
        timeStamps = [self.time,self.time,self.time-timezone.timedelta(minutes=11)]

        for cont in range(3):
            devicePosition = DevicePositionInTime.objects.get(longitud = longituds[cont])
            self.assertEqual(devicePosition.latitud, latituds[cont])
            self.assertEqual(devicePosition.timeStamp, timeStamps[cont])

    def test_consistencyModelActiveToken(self):
        '''This method test the database for the ActiveToken model'''
        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        reponseView = RequestToken()
        response = reponseView.get(request, self.userId, '503', 'ZZZZ00')

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        testToken = testToken['token']

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)

        request = self.factory.get('/android/endRoute/' + testToken)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,testToken)

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'], 'Trip ended.')

    def test_consistencyModelPoseInTrajectoryOfToken(self):
        '''this method test the PoseInTrajectoryOfToken'''

        testPoses = {"poses":[\
                {"latitud":-33.458771,"longitud" : -70.676266, "timeStamp":"2015-10-01T18:10:00", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458699,"longitud" : -70.675708, "timeStamp":"2015-10-01T18:10:10", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458646,"longitud" : -70.674678, "timeStamp":"2015-10-01T18:10:15", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458646,"longitud" : -70.673799, "timeStamp":"2015-10-01T18:10:20", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458413,"longitud" : -70.671631, "timeStamp":"2015-10-01T18:10:24", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457983,"longitud" : -70.669035, "timeStamp":"2015-10-01T18:10:30", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457518,"longitud" : -70.666718, "timeStamp":"2015-10-01T18:10:35", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457196,"longitud" : -70.664636, "timeStamp":"2015-10-01T18:10:40", "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457070,"longitud" : -70.660559, "timeStamp":"2015-10-01T18:10:50", "inVehicleOrNot":"vehicle"}]}

        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        reponseView = RequestToken()
        response = reponseView.get(request, self.userId, '503','ZZZZ00')

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        testToken = testToken['token']

        request = self.factory.get('/android/sendTrajectoy')
        request.user = AnonymousUser()

        reponseView = SendPoses()
        request.POST = {}
        request.POST['pToken'] = testToken
        request.POST['pTrajectory'] = json.dumps(testPoses)
        request.method = 'POST'
        response = reponseView.post(request)

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'],'Poses were register.')

        # remove the token
        request = self.factory.get('/android/endRoute/' + testToken)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,testToken)

        request = self.factory.get('/android/sendTrajectoy')
        request.user = AnonymousUser()

        reponseView = SendPoses()
        request.POST = {}
        request.POST['pToken'] = testToken
        request.POST['pTrajectory'] = json.dumps(testPoses)
        request.method = 'POST'
        response = reponseView.post(request)

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'],'Token doesn\'t exist.')

    def test_EndRoute(self):
        '''this method test the EndRoute request when it fails.'''
        request = self.factory.get('/android/endRoute/')
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,'01234567890123456789012345678901234567890\
                123456789012345678901234567890123456789012345678901234567890123456789012345678901234567')

        contentResponse = json.loads(response.content)
        contentResponse = contentResponse['response']

        self.assertEqual(contentResponse,'Token doesn\'t exist.')

    def test_EventsByBusWithDummyLicensePlate(self):
        '''This method test the bus with a dummy license plate '''

        licencePlate = Constants.DUMMY_LICENSE_PLATE
        busService = '507'
        eventCode = 'evn00101'

        # submitting one event to the server
        requestToReportEventBus = self.factory.get('/android/reportEventBus/')
        requestToReportEventBus.user = AnonymousUser()

        reportEventBusView = RegisterEventBus()

        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, busService, licencePlate, eventCode, 'confirm')

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['service'], busService)
        self.assertEqual(len(responseToReportEventBus['events']), 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

    def test_EventsByBus(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific bus'''

        licencePlate = 'AA0000'
        busService = '507'
        eventCode = 'evn00101'

        # submitting one event to the server
        requestToReportEventBus = self.factory.get('/android/reportEventBus/')
        requestToReportEventBus.user = AnonymousUser()

        reportEventBusView = RegisterEventBus()
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, busService, licencePlate, eventCode, 'confirm')

        responseToReportEventBus = json.loads(responseToReportEventBus.content)


        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        requestToRequestEventForBus = self.factory.get('/android/requestEventsForBus/')
        requestToRequestEventForBus.user = AnonymousUser()

        # verify the previous event reported
        requestEventForBusView = EventsByBus()
        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus, \
                licencePlate, busService)

        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)



        self.assertEqual(responseToRequestEventForBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToRequestEventForBus['service'], busService)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # do event +1 to the event
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, self.userId,\
                busService, licencePlate, eventCode, 'confirm')
        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,\
                licencePlate, busService)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus['registrationPlate'],licencePlate)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'],0)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'],2)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'],eventCode)

        # do event -1 to the event
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, self.userId, \
                busService, licencePlate, eventCode, 'decline')
        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,\
                licencePlate,busService)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'], eventCode)

        # change manually the timeStamp to simulate an event that has expired
        #bus= Bus.objects.get(registrationPlate=licencePlate, service=busService)
        bus = Busv2.objects.get(registrationPlate=licencePlate)
        busassignment = Busassignment.objects.get(uuid=bus, service=busService)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusv2.objects.get(busassignment=busassignment,event=event)

        anEvent.timeStamp = anEvent.timeCreation - timezone.timedelta(minutes=event.lifespam)
        anEvent.save()

        # ask for events and the answer should be none
        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus, licencePlate,busService)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(len(responseToRequestEventForBus['events']),0)

    def test_EventsByBusStop(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific busStop'''

        busStopCode = 'PA459'
        eventCode = 'evn00001'
        # submitting some events to the server
        request = self.factory.get('/android/reportEventBusStop/')
        request.user = AnonymousUser()

        request0 = self.factory.get('/android/requestEventsForBusStop/')
        request0.user = AnonymousUser()

        reponseView = RegisterEventBusStop()
        response = reponseView.get(request, self.userId, busStopCode, eventCode, 'confirm')

        # report one event, and confirm it
        response0View = EventsByBusStop()
        response0 = response0View.get(request0,busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0['codeBusStop'],busStopCode)
        self.assertEqual(response0['events'][0]['eventDecline'],0)
        self.assertEqual(response0['events'][0]['eventConfirm'],1)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)


        # do event +1 to the event
        response = reponseView.get(request,self.userId, busStopCode,eventCode,'confirm')
        response0 = response0View.get(request0,busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0['codeBusStop'],busStopCode)
        self.assertEqual(response0['events'][0]['eventDecline'],0)
        self.assertEqual(response0['events'][0]['eventConfirm'],2)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)

        # do event -1 to the event
        response = reponseView.get(request, self.userId, busStopCode,eventCode,'decline')
        response0 = response0View.get(request0,busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0['codeBusStop'],busStopCode)
        self.assertEqual(response0['events'][0]['eventDecline'],1)
        self.assertEqual(response0['events'][0]['eventConfirm'],2)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)

        # change manualy the timeStamp to simulate an event that has expired
        busStop= BusStop.objects.get(code=busStopCode)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusStop.objects.get(busStop=busStop,event=event)

        anEvent.timeStamp = anEvent.timeCreation - timezone.timedelta(minutes=event.lifespam)
        anEvent.save()

        # ask for ecents and the answere should be none
        response0 = response0View.get(request0,busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(len(response0['events']),0)

    def test_registerPose(self):
        request = self.factory.get('/android/userPosition')
        request.user = AnonymousUser()
        lat = 45
        lon = 46
        response = views.userPosition(request, self.userId, lat, lon)

        self.assertEqual(response.status_code,200)

        self.assertEqual(DevicePositionInTime.objects.filter(longitud=lon, latitud=lat).exists(), True)


    def test_nearbyBuses(self):
        request = self.factory.get('/android/nearbyBuses')
        request.user = AnonymousUser()

        busStopCodeThis = 'PA459'

        busStop = BusStop.objects.get(code = busStopCodeThis)
        service = Service.objects.get(service = '507')
        serviceCode = '507R'

        ServicesByBusStop.objects.create(busStop = busStop, service= service, code = serviceCode)
        ServiceStopDistance.objects.create(busStop = busStop, service = serviceCode, distance = 124529)

        response = views.nearbyBuses(request, self.userId, busStopCodeThis)

        self.assertEqual(response.status_code,200)

        jsonResponse = json.loads(response.content)

        if (jsonResponse['DTPMError'] != ""):
            self.assertEqual(jsonResponse['DTPMError'], \
                    "Usted no cuenta con los permisos necesarios para realizar esta consulta.")
        else:
            self.assertEqual('servicios' in jsonResponse, True)
            self.assertEqual('eventos' in jsonResponse, True)

    def test_formatServiceName(self):
        serviceName1 = "506E"
        serviceName2 = "506N"
        serviceName3 = "D03N"
        serviceName4 = "D03E"
        serviceName5 = "D03"
        serviceName6 = "N50"
        serviceName7 = "506"

        self.assertEqual(views.formatServiceName(serviceName1), "506e")
        self.assertEqual(views.formatServiceName(serviceName2), "506N")
        self.assertEqual(views.formatServiceName(serviceName3), "D03N")
        self.assertEqual(views.formatServiceName(serviceName4), "D03e")
        self.assertEqual(views.formatServiceName(serviceName5), "D03")
        self.assertEqual(views.formatServiceName(serviceName6), "N50")
        self.assertEqual(views.formatServiceName(serviceName7), "506")

    def test_preferPositionOfPersonInsideABus(self):

        #Bus.objects.create(registrationPlate = 'AA1111', service = '507')
        thebus = Busv2.objects.create(registrationPlate = 'AA1111')
        Busassignment.objects.create(service = '507', uuid=thebus)

        timeStampNow = str(timezone.localtime(timezone.now()))
        timeStampNow = timeStampNow[0:19]
        userLatitud = -33.458771
        userLongitud = -70.676266

        # first we test the position of the bus without passsangers
        #bus = Bus.objects.get(registrationPlate='AA1111', service='507')
        bus = Busv2.objects.get(registrationPlate='AA1111')
        busassignment = Busassignment.objects.get(service='507', uuid=bus)

        busPose = busassignment.getLocation()

        self.assertTrue(busPose['random'])
        self.assertEqual(busPose['latitude'], -500)
        self.assertEqual(busPose['longitude'], -500)
        self.assertEqual(busPose['passengers'], 0)

        # add the position of a passanger inside the bus
        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        reponseView = RequestToken()
        response = reponseView.get(request, self.userId, '507','AA1111')

        testToken = json.loads(response.content)
        testToken = testToken['token']

        testPoses = {"poses":[
            {"latitud": userLatitud, "longitud" : userLongitud, "timeStamp":str(timeStampNow), "inVehicleOrNot":"vehicle"}]}

        request = self.factory.get('/android/sendTrajectoy')
        request.user = AnonymousUser()
        request.POST = {}
        request.POST['pToken'] = testToken
        request.POST['pTrajectory'] = json.dumps(testPoses)
        request.method = 'POST'
        reponseView = SendPoses()
        response = reponseView.post(request)

        # ask the position of the bus whit a passanger
        bus = Busv2.objects.get(registrationPlate='AA1111')
        busassignment = Busassignment.objects.get(uuid = bus, service='507')

        busPose = busassignment.getLocation()

        self.assertEqual(busPose['latitude'], userLatitud)
        self.assertEqual(busPose['longitude'], userLongitud)
        self.assertEqual(busPose['random'], False)
        self.assertEqual(busPose['passengers'] > 0, True)

        reponseView = EndRoute()
        response = reponseView.get(request,testToken)


