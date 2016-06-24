from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

# python stuf
import json

# model
from AndroidRequests.models import Event, BusStop
# view
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop
from AndroidRequests.allviews.EventsByBus import EventsByBus
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop

# functions to test
import AndroidRequests.cronTasks as cronTasks

class CronTasksTestCase(TestCase):
    """ test for cron-task actions """
    def setUp(self):
        self.factory = RequestFactory()

        # create bus stop
        self.busStopCode = 'PI62'
        BusStop.objects.create(code=self.busStopCode, name = 'dummy bus stop', latitud='100', longitud='100')

        # create a group of events
        self.busStopEventId = 'ebs'
        Event.objects.create(id=self.busStopEventId, name='event for bus stop', \
                description='event for bus stop from bus stop', eventType='busStop', origin='o', lifespam='20')
        self.busEventId = 'bfb'
        Event.objects.create(id=self.busEventId, name='event for bus', \
                description='event for bus from bus', eventType='bus', origin='i', lifespam='10')

        self.userId = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.busService = '506'
        self.registrationPlate = 'XXYY25'

    def test_does_not_have_the_minimum_number_of_declines_for_bus_stop(self):
        """ it does not have the minimum number of declines for bus stop """

        urlBusStop = 'android/reportEventBusStop'
        busStopRequest = self.factory.get(urlBusStop)
        busStopRequest.user = AnonymousUser()
        busStopResponseView = RegisterEventBusStop()

        # report events for bus stop
        busStopResponseView.get(busStopRequest, self.userId, self.busStopCode, self.busStopEventId, 'confirm')

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES-1):
            busStopResponseView.get(busStopRequest, self.userId, self.busStopCode, self.busStopEventId, 'decline')
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        urlEventsByBus = 'android/requestEventsForBusStop'
        eventsByBusStopRequest = self.factory.get(urlEventsByBus)
        responseView = EventsByBusStop()
        response = responseView.get(eventsByBusStopRequest, self.busStopCode)
        jsonResponse = json.loads(response.content)

        # evaluate events
        self.assertEqual(len(jsonResponse['events']), 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.busStopEventId)

    def test_does_not_have_the_percentage_of_declines_for_bus_stop(self):
        """ it has the minimum number of declines but not the percentage of declines over confirms for bus stop"""

        urlBusStop = 'android/reportEventBusStop'
        busStopRequest = self.factory.get(urlBusStop)
        busStopRequest.user = AnonymousUser()
        busStopResponseView = RegisterEventBusStop()

        # report events for bus stop
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES+1):
            busStopResponseView.get(busStopRequest, self.userId, self.busStopCode, self.busStopEventId, 'confirm')

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES+1):
            busStopResponseView.get(busStopRequest, self.userId, self.busStopCode, self.busStopEventId, 'decline')
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        urlEventsByBus = 'android/requestEventsForBusStop'
        eventsByBusStopRequest = self.factory.get(urlEventsByBus)
        responseView = EventsByBusStop()
        response = responseView.get(eventsByBusStopRequest, self.busStopCode)
        jsonResponse = json.loads(response.content)

        # evaluate events
        self.assertEqual(len(jsonResponse['events']), 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.busStopEventId)

    def test_have_the_percentage_of_declines_and_the_minimum_number_of_declines_over_confirm_for_bus_stop(self):
        """ it has the minimum number of declines and the percentage of declines over confirms for bus stop"""

        urlBusStop = 'android/reportEventBusStop'
        busStopRequest = self.factory.get(urlBusStop)
        busStopRequest.user = AnonymousUser()
        busStopResponseView = RegisterEventBusStop()

        # report events for bus stop
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES):
            busStopResponseView.get(busStopRequest, self.userId, self.busStopCode, self.busStopEventId, 'confirm')

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES*3):
            busStopResponseView.get(busStopRequest, self.userId, self.busStopCode, self.busStopEventId, 'decline')
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        urlEventsByBus = 'android/requestEventsForBusStop'
        eventsByBusStopRequest = self.factory.get(urlEventsByBus)
        responseView = EventsByBusStop()
        response = responseView.get(eventsByBusStopRequest, self.busStopCode)
        jsonResponse = json.loads(response.content)

        # evaluate events
        self.assertEqual(len(jsonResponse['events']), 0)

    def test_does_not_have_the_minimum_number_of_declines_for_bus(self):
        """ it does not have the minimum number of declines for bus  """

        urlBus = 'android/reportEventBus'
        busRequest = self.factory.get(urlBus)
        busRequest.user = AnonymousUser()
        busResponseView = RegisterEventBus()
        # report events for bus
        busResponseView.get(busRequest, self.userId, self.busService, self.registrationPlate, self.busEventId, 'confirm')

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES-1):
            busResponseView.get(busRequest, self.userId, self.busService, self.registrationPlate, self.busEventId, 'decline')
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        urlEventsByBus = 'android/requestEventsForBus'
        eventsByBusRequest = self.factory.get(urlEventsByBus)
        responseView = EventsByBus()
        response = responseView.get(eventsByBusRequest, self.registrationPlate, self.busService)
        jsonResponse = json.loads(response.content)

        # evaluate events
        self.assertEqual(len(jsonResponse['events']), 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.busEventId)

    def test_does_not_have_the_percentage_of_declines_for_bus(self):
        """ it has the minimum number of declines but not the percentage of declines over confirms for bus """

        urlBus = 'android/reportEventBus'
        busRequest = self.factory.get(urlBus)
        busRequest.user = AnonymousUser()
        busResponseView = RegisterEventBus()
        # generate report events for bus
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES+1):
            busResponseView.get(busRequest, self.userId, self.busService, self.registrationPlate, self.busEventId, 'confirm')

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES+1):
            busResponseView.get(busRequest, self.userId, self.busService, self.registrationPlate, self.busEventId, 'decline')
        # decline is 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        urlEventsByBus = 'android/requestEventsForBus'
        eventsByBusRequest = self.factory.get(urlEventsByBus)
        responseView = EventsByBus()
        response = responseView.get(eventsByBusRequest, self.registrationPlate, self.busService)
        jsonResponse = json.loads(response.content)

        # evaluate events
        self.assertEqual(len(jsonResponse['events']), 1)
        self.assertEqual(jsonResponse['events'][0]['eventcode'], self.busEventId)

    def test_have_the_percentage_of_declines_and_the_minimum_number_of_declines_over_confirm_for_bus(self):
        """ it has the minimum number of declines and the percentage of declines over confirms for bus """

        urlBus = 'android/reportEventBus'
        busRequest = self.factory.get(urlBus)
        busRequest.user = AnonymousUser()
        busResponseView = RegisterEventBus()
        # generate report events for bus
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES):
            busResponseView.get(busRequest, self.userId, self.busService, self.registrationPlate, self.busEventId, 'confirm')

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES*3):
            busResponseView.get(busRequest, self.userId, self.busService, self.registrationPlate, self.busEventId, 'decline')
        # decline is 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        urlEventsByBus = 'android/requestEventsForBus'
        eventsByBusRequest = self.factory.get(urlEventsByBus)
        responseView = EventsByBus()
        response = responseView.get(eventsByBusRequest, self.registrationPlate, self.busService)
        jsonResponse = json.loads(response.content)

        # evaluate events
        self.assertEqual(len(jsonResponse['events']), 0)


