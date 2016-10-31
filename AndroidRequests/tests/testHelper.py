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
from AndroidRequests.allviews.RegisterEventBusV2 import RegisterEventBusV2
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.RequestTokenV2 import RequestTokenV2
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.RequestUUID import RequestUUID
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
        response = view.get(request, self.userId, busService, machineId)

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

