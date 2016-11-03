from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json
import re

from AndroidRequests.models import *

# views
from AndroidRequests.allviews.BusStopsByService import BusStopsByService
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.RegisterEventBusV2 import RegisterEventBusV2
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RequestTokenV2 import RequestTokenV2
from AndroidRequests.allviews.RequestUUID import RequestUUID
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.RequestUUID import RequestUUID
import AndroidRequests.views as views
import AndroidRequests.constants as Constants

from AndroidRequests.tests.testHelper import TestHelper

class DummyLicensePlateUUIDTest(TestCase):

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.userId2 = "4f20c8f4-ddea-4c6c-87bb-c7bd3d435a51"

        #loads the events
        self.helper = TestHelper(self)
        self.helper.insertEventsOnDatabase()

        # add dummy  bus
        b1 = Busv2.objects.create(registrationPlate = 'AA1111', uuid = '159fc6b7-7a20-477e-b5c7-af421e1e0e16')
        # add bus assignment
        ba1 = Busassignment.objects.create(service = '507', uuid = b1)

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

        machineId = self.helper.askForMachineId(licencePlate)

        #a ghost bus is created with the same uuid that was recieved
        self.assertEqual(Busv2.objects.filter(uuid=machineId).exists(), True)

        testToken = self.helper.getInBusWithMachineId(self.userId, busService, machineId)

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)
 
        jsonResponse = self.helper.endRoute(testToken)
        
        self.assertEqual(jsonResponse['response'], 'Trip ended.')

    def test_RequestTokenV2WithRealLicencePlate(self):
        ''' This method will test a token for bus with uuid '''

        licencePlate = 'AA1111'
        busService = '507'

        machineId = self.helper.askForMachineId(licencePlate)

        #a ghost bus is created with the same uuid that was recieved
        self.assertEqual(Busv2.objects.filter(uuid=machineId).exists(), True)

        testToken = self.helper.getInBusWithMachineId(self.userId, busService, machineId)

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)
        
        jsonResponse = self.helper.endRoute(testToken)       

        self.assertEqual(jsonResponse['response'], 'Trip ended.')

    def test_EventsByBusWithDummyLicensePlateUUID(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific dummy bus'''

        licencePlate = Constants.DUMMY_LICENSE_PLATE
        busService = '507'
        eventCode = 'evn00101'

        machineId = self.helper.askForMachineId(licencePlate)

        #a ghost bus is created with the same uuid that was recieved
        self.assertEqual(Busv2.objects.filter(uuid=machineId).exists(), True)

        testToken = self.helper.getInBusWithMachineId(self.userId, busService, machineId)

        # the created token is an active token
        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)
        # the created token exist in the table of token
        self.assertEqual(Token.objects.filter(token=testToken).exists(), True)
        #the created token has the uuid for the dummybus
        #self.assertEqual(Token.objects.filter(uuid=puuid).exists(), True)
        
        # submitting one event to the server
        jsonResponse = self.helper.reportEventV2(self.userId, machineId, busService, eventCode)

        self.assertEqual(jsonResponse['uuid'], machineId)
        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        jsonResponse = self.helper.requestEventsForBusV2(machineId)

        # verify the previous event reported
        self.assertEqual(jsonResponse['uuid'], machineId)
        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # do event +1 to the event
        jsonResponse = self.helper.confirmOrDeclineEventV2(self.userId, machineId, busService, \
                       eventCode, 'confirm')
        
        self.assertEqual(jsonResponse['uuid'], machineId)
        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        jsonResponse = self.helper.requestEventsForBusV2(machineId)

        # verify the previous event reported
        self.assertEqual(jsonResponse['uuid'], machineId)
        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 0)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # do event -1 to the event
        jsonResponse = self.helper.confirmOrDeclineEventV2(self.userId, machineId, busService, \
                       eventCode, 'decline')

        self.assertEqual(jsonResponse['uuid'], machineId)
        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        jsonResponse = self.helper.requestEventsForBusV2( machineId)

        # verify the previous event reported
        self.assertEqual(jsonResponse['uuid'], machineId)
        self.assertEqual(jsonResponse['registrationPlate'], licencePlate)
        self.assertEqual(jsonResponse['events'][0]['eventDecline'], 1)
        self.assertEqual(jsonResponse['events'][0]['eventConfirm'], 2)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], eventCode)

        # change manually the timeStamp to simulate an event that has expired
        bus= Busv2.objects.get(uuid=machineId)
        assignment= Busassignment.objects.get(service=busService, uuid=bus)
        event = Event.objects.get(id=eventCode)
        anEvent = EventForBusv2.objects.get(busassignment=assignment,event=event)

        anEvent.timeStamp = anEvent.timeCreation - timezone.timedelta(minutes=event.lifespam)
        anEvent.save()

        # ask for events and the answer should be none
        jsonResponse = self.helper.requestEventsForBusV2(machineId)

        self.assertEqual(len(jsonResponse['events']),0)

    def test_EventsByBusv2(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific bus'''

        licencePlate = 'AA1111'
        busService = '507'
        eventCode = 'evn00101'

        getUUID = self.factory.get('/android/getUUID/')
        #getUUID.user = AnonymousUser()
        getUUIDView = RequestUUID()
        responseGetUUID = getUUIDView.get(getUUID,licencePlate)

        self.assertEqual(responseGetUUID.status_code, 200)
        
        testGet = json.loads(responseGetUUID.content)
        testGetUUID = testGet['uuid']

        # submitting one event to the server
        requestToReportEventBus = self.factory.get('/android/reportEventBus/v2/')
        requestToReportEventBus.user = AnonymousUser()

        reportEventBusView = RegisterEventBusV2()

        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, testGetUUID, busService, eventCode, 'confirm')

        responseToReportEventBus = json.loads(responseToReportEventBus.content)


        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # getting events for a specific bus
        requestToRequestEventForBus = self.factory.get('/android/requestEventsForBus/v2/')
        requestToRequestEventForBus.user = AnonymousUser()

        # verify the previous event reported
        requestEventForBusView = EventsByBusV2()
        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus, \
                testGetUUID)

        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)



        self.assertEqual(responseToRequestEventForBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'], eventCode)

        # ===================================================================================
        # do event +1 to the event
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, self.userId,\
                testGetUUID, busService, eventCode, 'confirm')
        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,\
                testGetUUID)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(responseToRequestEventForBus['registrationPlate'],licencePlate)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventDecline'],0)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventConfirm'],2)
        self.assertEqual(responseToRequestEventForBus['events'][0]['eventcode'],eventCode)

        # do event -1 to the event
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, self.userId, \
                testGetUUID, busService, eventCode, 'decline')
        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 2)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode)

        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus,\
                testGetUUID)
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
        responseToRequestEventForBus = requestEventForBusView.get(requestToRequestEventForBus, bus.uuid)
        responseToRequestEventForBus = json.loads(responseToRequestEventForBus.content)

        self.assertEqual(len(responseToRequestEventForBus['events']),0)

    def test_EventsByBusStopv2(self):
        '''This method test two thing, the posibility to report an event and asking
        the events for the specific busStop'''

        busStopCode = 'PA459'
        eventCode = 'evn00001'
        # submitting some events to the server
        request = self.factory.get('/android/reportEventBusStop/v2/')
        request.user = AnonymousUser()

        request0 = self.factory.get('/android/requestEventsForBusStop/v2/')
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

    def test_RequestUUIDBasedOnLicensePlate(self):
        """ test the method to request an uuid based on license plate """
        licensePlates = ["AFJG21", "aFAf21", "AF-SD23", "FG-DF-45"]

        request = self.factory.get('/android/getUUID/')
        request.user = AnonymousUser()

        reponseView = RequestUUID()

        # it is a valid uuid
        pattern = re.compile("^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")

        for licensePlate in licensePlates:
            response = reponseView.get(request, licensePlate)

            self.assertEqual(response.status_code, 200)

            testUUID = json.loads(response.content)
            uuid = testUUID['uuid']
            
            self.assertTrue((pattern.match(uuid.upper()) if True else False))

        """ if request a second uuid with an old license plate, i must to get the same uuid """
        response2 = reponseView.get(request, licensePlates[3])
        testUUID2 = json.loads(response.content)
        uuid2 = testUUID2['uuid']

        self.assertTrue(pattern.match(uuid2.upper()))
        self.assertTrue(uuid == uuid2)

    def test_RequestUUIDBasedOnDummyLicensePlate(self):
        """ test the method to request an uuid based on dummy license plate """
        licensePlate = Constants.DUMMY_LICENSE_PLATE

        request = self.factory.get('/android/getUUID/')
        request.user = AnonymousUser()

        reponseView = RequestUUID()
        response = reponseView.get(request, licensePlate)

        self.assertEqual(response.status_code, 200)

        testUUID = json.loads(response.content)
        uuid = testUUID['uuid']
        
        # it is a valid uuid
        pattern = re.compile("^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")
        self.assertTrue((pattern.match(uuid.upper()) if True else False))

        """ if request a second uuid wiht dummy license plate, i must to get a new uuid """
        response2 = reponseView.get(request, licensePlate)
        testUUID2 = json.loads(response.content)
        uuid2 = testUUID2['uuid']

        self.assertTrue((pattern.match(uuid2.upper()) if True else False))
        self.assertTrue(uuid == uuid2)

    def test_MergeEventsFromTheSameBusButDifferenceService(self):
        """ test the method that merge event from the same bus machine but difference service """

        licencePlate = 'AA1111'
        busService1 = '506'
        busService2 = '509'
        eventCode1 = 'evn00230'
        eventCode2 = 'evn00240'
        eventCode3 = 'evn00232'

        # ask for bus and get the UUID
        request = self.factory.get('/android/getUUID/')
        view = RequestUUID()
        responseGetUUID = view.get(request, licencePlate)

        self.assertEqual(responseGetUUID.status_code, 200)
        
        testUUID = json.loads(responseGetUUID.content)['uuid']
  
        # creat bus to create an assignment
        request = self.factory.get('/android/requestToken/v2/')
        request.user = AnonymousUser()
        reponseView = RequestTokenV2()
        response = reponseView.get(request, self.userId, busService1, testUUID)
        self.assertEqual(response.status_code, 200)
 
        # creat bus to create an assignment
        request = self.factory.get('/android/requestToken/v2/')
        request.user = AnonymousUser()
        reponseView = RequestTokenV2()
        response = reponseView.get(request, self.userId, busService2, testUUID)
        self.assertEqual(response.status_code, 200)
      
        # submitting some events to the server
        requestToReportEventBus = self.factory.get('/android/reportEventBus/v2/')
        requestToReportEventBus.user = AnonymousUser()

        # send first report with service 1
        reportEventBusView = RegisterEventBusV2()
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, testUUID, busService1, eventCode1, 'confirm')

        responseToReportEventBus = json.loads(responseToReportEventBus.content)
        
        self.assertEqual(responseToReportEventBus['uuid'], testUUID)
        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode1)

        # send second report with service 2- We declien the previous event reportd
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, testUUID, busService2, eventCode1, 'decline')

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['uuid'], testUUID)
        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode1)

        # report second event to service
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, testUUID, busService1, eventCode2, 'confirm')

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['uuid'], testUUID)
        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode1)
        self.assertEqual(responseToReportEventBus['events'][1]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][1]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][1]['eventcode'], eventCode2)

        # report third event to service 
        responseToReportEventBus = reportEventBusView.get(requestToReportEventBus, \
                self.userId, testUUID, busService2, eventCode3, 'confirm')

        responseToReportEventBus = json.loads(responseToReportEventBus.content)

        self.assertEqual(responseToReportEventBus['uuid'], testUUID)
        self.assertEqual(responseToReportEventBus['registrationPlate'], licencePlate)
        self.assertEqual(responseToReportEventBus['events'][0]['eventDecline'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][0]['eventcode'], eventCode1)
        self.assertEqual(responseToReportEventBus['events'][1]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][1]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][1]['eventcode'], eventCode3)
        self.assertEqual(responseToReportEventBus['events'][2]['eventDecline'], 0)
        self.assertEqual(responseToReportEventBus['events'][2]['eventConfirm'], 1)
        self.assertEqual(responseToReportEventBus['events'][2]['eventcode'], eventCode2)






