from django.test import TransactionTestCase, RequestFactory

from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import EventRegistration

import AndroidRequests.cronTasks as cronTasks


class CronTasksTestCase(TransactionTestCase):
    """ test for cron-task actions """
    fixtures = ["events"]

    def setUp(self):
        self.factory = RequestFactory()

        self.test = TestHelper(self)

        # create bus stop
        self.stop = 'PI62'
        self.test.insertBusstopsOnDatabase([self.stop])

        # define test events
        self.stopEventCode = 'evn00010'
        self.busEventCode = 'evn00200'

        self.phone_id = '067e6162-3b6f-4ae2-a171-2470b63dff00'
        self.service = '506'
        self.registrationPlate = 'XXYY25'
        self.machineId = self.test.askForMachineId(self.registrationPlate)

    def test_does_not_have_the_minimum_number_of_declines_for_bus_stop(self):
        """ it does not have the minimum number of declines for bus stop """

        import time
        time.sleep(60)
        self.test.reportStopEvent(self.phone_id, self.stop, self.stopEventCode)

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES - 2):
            self.test.confirmOrDeclineStopEvent(
                self.phone_id, self.stop, self.stopEventCode, EventRegistration.DECLINE)
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        json_response = self.test.requestEventsForBusStop(self.stop)

        # evaluate events
        self.assertEqual(len(json_response['events']), 1)
        self.assertEqual(
            json_response['events'][0]['eventcode'],
            self.stopEventCode)

    def test_does_not_have_the_percentage_of_declines_for_bus_stop(self):
        """ it has the minimum number of declines but not the percentage of declines over confirms for bus stop"""

        self.test.reportStopEvent(self.phone_id, self.stop, self.stopEventCode)

        # report events for bus stop
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES + 1):
            self.test.confirmOrDeclineStopEvent(
                self.phone_id, self.stop, self.stopEventCode, EventRegistration.CONFIRM)

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES + 1):
            self.test.confirmOrDeclineStopEvent(
                self.phone_id, self.stop, self.stopEventCode, EventRegistration.DECLINE)
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        json_response = self.test.requestEventsForBusStop(self.stop)

        # evaluate events
        self.assertEqual(len(json_response['events']), 1)
        self.assertEqual(
            json_response['events'][0]['eventcode'],
            self.stopEventCode)

    def test_have_the_percentage_of_declines_and_the_minimum_number_of_declines_over_confirm_for_bus_stop(
            self):
        """ it has the minimum number of declines and the percentage of declines over confirms for bus stop"""

        self.test.reportStopEvent(self.phone_id, self.stop, self.stopEventCode)

        # report events for bus stop
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES):
            self.test.confirmOrDeclineStopEvent(
                self.phone_id, self.stop, self.stopEventCode, EventRegistration.CONFIRM)

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES * 3):
            self.test.confirmOrDeclineStopEvent(
                self.phone_id, self.stop, self.stopEventCode, EventRegistration.DECLINE)
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        json_response = self.test.requestEventsForBusStop(self.stop)
        # evaluate events
        self.assertEqual(len(json_response['events']), 0)

    def test_does_not_have_the_minimum_number_of_declines_for_bus(self):
        """ it does not have the minimum number of declines for bus  """
        # create assignment
        self.test.createBusAndAssignmentOnDatabase(
            self.phone_id, self.service, self.registrationPlate)

        self.test.reportEventV2(
            self.phone_id,
            self.machineId,
            self.service,
            self.busEventCode)

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES - 1):
            self.test.confirmOrDeclineEventV2(
                self.phone_id,
                self.machineId,
                self.service,
                self.busEventCode,
                EventRegistration.DECLINE)
        # decline isn't 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        json_response = self.test.requestEventsForBusV2(self.machineId)

        # evaluate events
        self.assertEqual(len(json_response['events']), 1)
        self.assertEqual(
            json_response['events'][0]['eventcode'],
            self.busEventCode)
        self.assertEqual(json_response['uuid'], self.machineId)
        self.assertEqual(
            json_response['registrationPlate'],
            self.registrationPlate)

    def test_does_not_have_the_percentage_of_declines_for_bus(self):
        """ it has the minimum number of declines but not the percentage of declines over confirms for bus """

        # create assignment
        self.test.createBusAndAssignmentOnDatabase(
            self.phone_id, self.service, self.registrationPlate)
        # generate report events for bus
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES + 1):
            self.test.confirmOrDeclineEventV2(
                self.phone_id,
                self.machineId,
                self.service,
                self.busEventCode,
                EventRegistration.CONFIRM)
        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES + 1):
            self.test.confirmOrDeclineEventV2(
                self.phone_id,
                self.machineId,
                self.service,
                self.busEventCode,
                EventRegistration.DECLINE)
        # decline is 100% over confirm

        cronTasks.clearEventsThatHaveBeenDecline()

        json_response = self.test.requestEventsForBusV2(self.machineId)

        # evaluate events
        self.assertEqual(len(json_response['events']), 1)
        self.assertEqual(
            json_response['events'][0]['eventcode'],
            self.busEventCode)
        self.assertEqual(json_response['uuid'], self.machineId)
        self.assertEqual(
            json_response['registrationPlate'],
            self.registrationPlate)

    def test_have_the_percentage_of_declines_and_the_minimum_number_of_declines_over_confirm_for_bus(
            self):
        """ it has the minimum number of declines and the percentage of declines over confirms for bus """
        # create assignment
        self.test.createBusAndAssignmentOnDatabase(
            self.phone_id, self.service, self.registrationPlate)

        self.test.reportEventV2(
            self.phone_id,
            self.machineId,
            self.service,
            self.busEventCode)

        # generate report events for bus
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES):
            self.test.confirmOrDeclineEventV2(
                self.phone_id,
                self.machineId,
                self.service,
                self.busEventCode,
                EventRegistration.CONFIRM)

        # decline event
        for index in range(0, cronTasks.MINIMUM_NUMBER_OF_DECLINES * 3):
            self.test.confirmOrDeclineEventV2(
                self.phone_id,
                self.machineId,
                self.service,
                self.busEventCode,
                EventRegistration.DECLINE)
        # decline is 100% over confirm

        json_response = self.test.requestEventsForBusV2(self.machineId)
        self.assertEqual(len(json_response['events']), 1)
        self.assertEqual(
            json_response['events'][0]['eventcode'],
            self.busEventCode)
        self.assertEqual(json_response['uuid'], self.machineId)

        cronTasks.clearEventsThatHaveBeenDecline()

        json_response = self.test.requestEventsForBusV2(self.machineId)

        # evaluate events
        self.assertEqual(len(json_response['events']), 0)
