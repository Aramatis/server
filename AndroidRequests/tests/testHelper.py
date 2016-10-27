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
from Loaders.LoaderFactory import LoaderFactory

class TestHelper():
    """ methods that help to create test cases """

    def __init__(self):
        self.factory = RequestFactory()

    def insertEventsOnDatabase(self):
         #loads the events

        log = open('loadDataErrorTest.log', 'w')

        csv = open('InitialData/events.csv', 'r') #path to Bus Stop csv file
        csv.next()
        factory = LoaderFactory()
        loader = factory.getModelLoader('event')(csv, log)
        loader.load()
        csv.close()
        log.close()

    def askForMachineId(self, testInstance, pLicencePlate):
        """ simulate a request to get machine id based on its licence plate """
        URL = '/android/getUUID/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()
        view = RequestUUID()
        response = view.get(request, pLicencePlate)

        testInstance.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        machineId = jsonResponse['uuid']
 
        return machineId

    def getInBusWithLicencePlate(self, testInstance, userId, service, licencePlate):
        """ create a user on bus in database """
        machineId = self.askForMachineId(licencePlate)

        URL = '/android/requestToken/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RequestTokenV2()
        response = view.get(request, self.userId, busService, machineId)

        testInstance.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']
 
        return token

    def getInBusWithMachineId(self, testInstance, userId, service, machineId):
        """ create a user on bus in database """

        URL = '/android/requestToken/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RequestTokenV2()
        response = view.get(request, userId, service, machineId)

        testInstance.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']
 
        return token

    def reportEvent(self, testInstance, userId, service, licencePlate, eventCode):
        pass

    def confirmOrDeclineEvent(self, testInstance, userId, machineId, service, eventCode, confirmOrDecline):
        pass

    def reportEventV2(self, testInstance, userId, machineId, service, eventCode):
        """ report an event with the new version  """
        URL = '/android/reportEventBus/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RegisterEventBusV2()
        response = view.get(request, userId, machineId, service, eventCode, 'confirm')

        testInstance.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse
   
    def confirmOrDeclineEventV2(self, testInstance, userId, machineId, service, eventCode, confirmOrDecline):
        """ confirm or decline an event with the new version  """
        URL = '/android/reportEventBus/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RegisterEventBusV2()
        response = view.get(request, userId, machineId, service, eventCode, confirmOrDecline)

        testInstance.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse
 
    def endRoute(self, testInstance, token):
        """ revoke token used to identify a trip """
        URL = '/android/endRoute/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request, token)

        testInstance.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def requestEventsForBusV2(self, testInstance, machineId):
        """ ask for events related to machine id """
        URL = '/android/requestEventsForBus/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        reponseView = EventsByBusV2()
        response = reponseView.get(request, machineId)

        testInstance.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

