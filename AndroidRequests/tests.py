from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json

# my stuff
from AndroidRequests.models import *
# views
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
import AndroidRequests.views as views
# Create your tests here.

class DevicePositionInTimeTest(TestCase):
    def setUp(self):
        # for testing requests inside the project
        self.factory = RequestFactory()

        # iniital config for DevicePositionInTime
        self.time = timezone.now()
        DevicePositionInTime.objects.create(longitud = 3.5, latitud = 5.2, timeStamp = self.time)
        DevicePositionInTime.objects.create(longitud = 3.4, latitud = 5.2, timeStamp = self.time)
        # this should not be answered
        DevicePositionInTime.objects.create(longitud = 3.3, latitud = 4.2, timeStamp = self.time\
        	-timezone.timedelta(minutes=11))        

        # initial config for ActiveToken

        #loads the events
        from Loaders.ModelLoaders import LoadEvents

        loadAllEvents = LoadEvents()
        loadAllEvents.loadEvents()

        # add one busStop
        BusStop.objects.create(code='PA459', name='bla',longitud=0,latitud=0)


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
        response = reponseView.get(request,'503','ZZZZ00')

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        testToken = testToken['token']

        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)
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
        response = reponseView.get(request,'503','ZZZZ00')

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        testToken = testToken['token']

        request = self.factory.get('/android/sendTrajectoy')
        request.user = AnonymousUser()

        reponseView = SendPoses()#pToken, pTrajectory
        response = reponseView.get(request,testToken,json.dumps(testPoses))

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'],'Poses were register.')

        # remove the token
        request = self.factory.get('/android/endRoute/' + testToken)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,testToken)

        request = self.factory.get('/android/sendTrajectoy')
        request.user = AnonymousUser()

        reponseView = SendPoses()#pToken, pTrajectory
        response = reponseView.get(request,testToken,json.dumps(testPoses))

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

    def test_EventsByBus(self):
        '''This method test two thing, the posibility to report an event and asking 
        the events for the specific bus'''

        licencePlate = 'AA0000'
        busService = '507'
        eventCode = 'evn00101'
        # submitting some events to the server
        request = self.factory.get('/android/reportEventBus/')
        request.user = AnonymousUser()

        request0 = self.factory.get('/android/requestEventsForBus/')
        request0.user = AnonymousUser()

        reponseView = RegisterEventBus()#request, pBusService, pBusPlate, pEventID, pConfirmDecline):
        response = reponseView.get(request,busService,licencePlate,eventCode,'confirm')

        # report one event, and confirm it
        response0View = EventsByBus()
        response0 = response0View.get(request0,licencePlate,busService)

        response0 = json.loads(response0.content)

        self.assertEqual(response0['registrationPlate'],licencePlate)
        self.assertEqual(response0['events'][0]['eventDecline'],0)
        self.assertEqual(response0['events'][0]['eventConfirm'],1)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)


        # do event +1 to the event
        response = reponseView.get(request,busService,licencePlate,eventCode,'confirm')
        response0 = response0View.get(request0, licencePlate,busService)
        response0 = json.loads(response0.content)

        self.assertEqual(response0['registrationPlate'],licencePlate)
        self.assertEqual(response0['events'][0]['eventDecline'],0)
        self.assertEqual(response0['events'][0]['eventConfirm'],2)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)

        # do event -1 to the event
        response = reponseView.get(request,busService,licencePlate,eventCode,'decline')
        response0 = response0View.get(request0, licencePlate,busService)
        response0 = json.loads(response0.content)

        self.assertEqual(response0['registrationPlate'],licencePlate)
        self.assertEqual(response0['events'][0]['eventDecline'],1)
        self.assertEqual(response0['events'][0]['eventConfirm'],2)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)

        # change manualy the timeStamp to simulate an event that has expired
        bus= Bus.objects.get(registrationPlate=licencePlate, service=busService)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBus.objects.get(bus=bus,event=event)

        anEvent.timeStamp = anEvent.timeCreation - timezone.timedelta(minutes=event.lifespam)
        anEvent.save()

        # ask for ecents and the answere should be none
        response0 = response0View.get(request0, licencePlate,busService)
        response0 = json.loads(response0.content)

        self.assertEqual(len(response0['events']),0)

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

        reponseView = RegisterEventBusStop()#request, pBusService, pBusPlate, pEventID, pConfirmDecline):
        response = reponseView.get(request,busStopCode,eventCode,'confirm')

        # report one event, and confirm it
        response0View = EventsByBusStop()
        response0 = response0View.get(request0,busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0['codeBusStop'],busStopCode)
        self.assertEqual(response0['events'][0]['eventDecline'],0)
        self.assertEqual(response0['events'][0]['eventConfirm'],1)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)


        # do event +1 to the event
        response = reponseView.get(request,busStopCode,eventCode,'confirm')
        response0 = response0View.get(request0,busStopCode)
        response0 = json.loads(response0.content)

        self.assertEqual(response0['codeBusStop'],busStopCode)
        self.assertEqual(response0['events'][0]['eventDecline'],0)
        self.assertEqual(response0['events'][0]['eventConfirm'],2)
        self.assertEqual(response0['events'][0]['eventcode'],eventCode)

        # do event -1 to the event
        response = reponseView.get(request,busStopCode,eventCode,'decline')
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
        response = views.userPosition(request, lat, lon)

        self.assertEqual(response.status_code,200)

        self.assertEqual(DevicePositionInTime.objects.filter(longitud=lon, latitud=lat).exists(), True)
