from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json

from AndroidRequests.models import *

# views
from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.SendPoses import SendPoses
import AndroidRequests.views as views
import AndroidRequests.constants as Constants

class DummyLicensePlateUUIDTest(TestCase):

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.userId2 = "4f20c8f4-ddea-4c6c-87bb-c7bd3d435a51"

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

    def test_RequestTokenWithDummyLicensePlateUUID(self):
        ''' This method will test a token for a dummy license plate bus with uuid '''

        licencePlate = Constants.DUMMY_LICENSE_PLATE
        busService = '507'

        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        reponseView = RequestToken()
        response = reponseView.get(request, self.userId, busService, licencePlate)

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        testUUID = testToken['uuid']
        testToken = testToken['token']

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)
        #the created token has the uuid for the dummybus
        self.assertEqual(Token.objects.filter(uuid=testUUID).exists(), True)
        #a ghost bus is created with the same uuid that was recieved in the token
        self.assertEqual(Bus.objects.filter(uuid=testUUID).exists(), True)

        request = self.factory.get('/android/endRoute/' + testToken)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,testToken)

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'], 'Trip ended.')

    def test_EventsByBusWithDummyLicensePlateUUID(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific dummy bus'''

        licencePlate = Constants.DUMMY_LICENSE_PLATE
        busService = '507'
        eventCode = 'evn00101'

        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        reponseView = RequestToken()
        response = reponseView.get(request, self.userId, busService, licencePlate)

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        puuid = testToken['uuid']
        testToken = testToken['token']

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)
        #the created token has the uuid for the dummybus
        self.assertEqual(Token.objects.filter(uuid=puuid).exists(), True)
        #a ghost bus is created with the same uuid that was recieved in the token
        self.assertEqual(Bus.objects.filter(uuid=puuid).exists(), True)

        # submitting one event to the server
        requestToReportEventBus = self.factory.get('/android/reportEventBus/')
        requestToReportEventBus.user = AnonymousUser()

        reportEventBusView = RegisterEventBus()
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, busService, licencePlate, eventCode, 'confirm', puuid=puuid)

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['service'], busService)
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
                licencePlate, busService, puuid=puuid)

        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToRequestEventForBus['service'], busService)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # do event +1 to the event
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, self.userId,\
                busService, licencePlate, eventCode, 'confirm', puuid=puuid)
        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['service'], busService)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,\
                licencePlate, busService, puuid=puuid)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus['registrationPlate'],licencePlate)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'],0)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'],2)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'],eventCode)

        # do event -1 to the event
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, self.userId, \
                busService, licencePlate, eventCode, 'decline', puuid=puuid)
        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['service'], busService)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,\
                licencePlate,busService, puuid=puuid)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'], eventCode)

        # change manually the timeStamp to simulate an event that has expired
        bus= Bus.objects.get(registrationPlate=licencePlate, service=busService, uuid=puuid)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBus.objects.get(bus=bus,event=event)

        anEvent.timeStamp = anEvent.timeCreation - timezone.timedelta(minutes=event.lifespam)
        anEvent.save()

        # ask for events and the answer should be none
        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,\
                licencePlate,busService, puuid=puuid)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(len(responseToRequestEventForBus['events']),0)