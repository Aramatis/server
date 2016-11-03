from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
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
from AndroidRequests.allviews.RegisterEventBusV2 import RegisterEventBusV2
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.RequestTokenV2 import RequestTokenV2
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.RequestUUID import RequestUUID
from AndroidRequests.allviews.SetDirection import SetDirection
import AndroidRequests.views as views
import AndroidRequests.constants as Constants

import os, sys
from Loaders.TestLoaderFactory import TestLoaderFactory

class TestHelper():
    """ methods that help to create test cases """

    def __init__(self, testInstance):
        self.factory = RequestFactory()
        self.test = testInstance

    def insertEventsOnDatabase(self):
        """ loads events """

        log = open('loadDataErrorTest.log', 'w')

        csv = open('InitialData/events.csv', 'r') #path to Bus Stop csv file
        csv.next()
        factory = TestLoaderFactory()
        loader = factory.getModelLoader('event')(csv, log)
        loader.load()
        csv.close()
        log.close()

    def insertServicesOnDatabase(self, serviceList):
        """ load services """

        log = open('loadDataErrorTest.log', 'w')

        csv = open('InitialData/services.csv', 'r') #path to Bus Stop csv file
        csv.next()
        factory = TestLoaderFactory()
        loader = factory.getModelLoader('service')(csv, log)
        loader.load(serviceList)
        csv.close()
        log.close()

    def insertBusstopsOnDatabase(self, busStopList):
        """ load bus stops """

        log = open('loadDataErrorTest.log', 'w')

        csv = open('InitialData/busstop.csv', 'r') #path to Bus Stop csv file
        csv.next()
        factory = TestLoaderFactory()
        loader = factory.getModelLoader('busstop')(csv, log)
        loader.load(busStopList)
        csv.close()
        log.close()

    def insertServicesByBusstopsOnDatabase(self, busStopList):
        """ load services by bus stops """

        log = open('loadDataErrorTest.log', 'w')

        csv = open('InitialData/servicesbybusstop.csv', 'r') #path to Bus Stop csv file
        csv.next()
        factory = TestLoaderFactory()
        loader = factory.getModelLoader('servicesbybusstop')(csv, log)
        loader.load(busStopList)
        csv.close()
        log.close()


    def askForMachineId(self, pLicencePlate):
        """ simulate a request to get machine id based on its licence plate """
        URL = '/android/getUUID/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()
        view = RequestUUID()
        response = view.get(request, pLicencePlate)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        machineId = jsonResponse['uuid']
 
        return machineId

    def createBusAndAssignmentOnDatabase(self, userId, service, licencePlate):
        """ create a bus object and assignment object """
        self.getInBusWithLicencePlate(userId, service, licencePlate)

    def getInBusWithLicencePlate(self, userId, service, licencePlate):
        """ create a user on bus in database """
        machineId = self.askForMachineId(licencePlate)

        URL = '/android/requestToken/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RequestTokenV2()
        response = view.get(request, userId, service, machineId)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']
 
        return token

    def getInBusWithMachineId(self, userId, service, machineId):
        """ create a user on bus in database """

        URL = '/android/requestToken/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RequestTokenV2()
        response = view.get(request, userId, service, machineId)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']
 
        return token

    def sendFakeTrajectoryOfToken(self, travelToken):
        """ send fake positions for user travel """

        URL = '/android/sendTrajectory'
        request = self.factory.post(URL)
        request.user = AnonymousUser()

        now = timezone.now()
        times = [now,\
                 now - timezone.timedelta(0, 5),\
                 now - timezone.timedelta(0, 10),\
                 now - timezone.timedelta(0, 15),\
                 now - timezone.timedelta(0, 20),\
                 now - timezone.timedelta(0, 25),\
                 now - timezone.timedelta(0, 30),\
                 now - timezone.timedelta(0, 35),\
                 now - timezone.timedelta(0, 40)]
        fTimes = []
        for time in times:
            fTimes.append(time.strftime("%Y-%m-%dT%X"))

        Poses = {"poses":[\
                {"latitud":-33.458771,"longitud" : -70.676266, "timeStamp": fTimes[0], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458699,"longitud" : -70.675708, "timeStamp": fTimes[1], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458646,"longitud" : -70.674678, "timeStamp": fTimes[2], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458646,"longitud" : -70.673799, "timeStamp": fTimes[3], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.458413,"longitud" : -70.671631, "timeStamp": fTimes[4], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457983,"longitud" : -70.669035, "timeStamp": fTimes[5], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457518,"longitud" : -70.666718, "timeStamp": fTimes[6], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457196,"longitud" : -70.664636, "timeStamp": fTimes[7], "inVehicleOrNot":"vehicle"},\
                {"latitud":-33.457070,"longitud" : -70.660559, "timeStamp": fTimes[8], "inVehicleOrNot":"vehicle"}]}


        view = SendPoses()
        request.POST = {}
        request.POST['pToken'] = travelToken
        request.POST['pTrajectory'] = json.dumps(Poses)
        request.method = 'POST'
        response = view.post(request)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        self.test.assertEqual(jsonResponse['response'],'Poses were register.')
        

    def reportEvent(self, userId, service, licencePlate, eventCode):
        pass

    def confirmOrDeclineEvent(self, userId, machineId, service, eventCode, confirmOrDecline):
        pass

    def reportEventV2(self, userId, machineId, service, eventCode):
        """ report an event with the new version  """
        URL = '/android/reportEventBus/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RegisterEventBusV2()
        response = view.get(request, userId, machineId, service, eventCode, 'confirm')

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse
   
    def confirmOrDeclineEventV2(self, userId, machineId, service, eventCode, confirmOrDecline):
        """ confirm or decline an event with the new version  """
        URL = '/android/reportEventBus/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RegisterEventBusV2()
        response = view.get(request, userId, machineId, service, eventCode, confirmOrDecline)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse
 
    def endRoute(self, token):
        """ revoke token used to identify a trip """
        URL = '/android/endRoute/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request, token)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def requestEventsForBusV2(self, machineId):
        """ ask for events related to machine id """
        URL = '/android/requestEventsForBus/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        reponseView = EventsByBusV2()
        response = reponseView.get(request, machineId)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def setDirection(self, travelKey, direction):
        """ set direction of trip """
        URL = '/android/setDirection/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        request.POST = {}
        request.POST['pToken'] = travelKey
        request.POST['pDirection'] = direction
        request.method = 'POST'

        view = SetDirection()
        response = view.post(request)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse
 
