from django.test import TransactionTestCase

from AndroidRequests.models import Level, ScoreEvent
from AndroidRequests.tests.testHelper import TestHelper


# Create your tests here.

class BusEventUserListTestCase(TransactionTestCase):
    """ test for user list returned by an event """

    def setUp(self):
        """ this method will automatically call for every single test """
        # create events
        self.test = TestHelper(self)
        self.test.insertEventsOnDatabase()
        self.eventCode = 'evn00201'

        # create levels 
        self.level = Level.objects.create(name='level 1', minScore=0, maxScore=1000, position=1)

        # create score event for eventCode
        self.score = 100
        ScoreEvent.objects.create(code=self.eventCode, score=self.score)

        self.phoneId = '1df6e1b6a1b840d689b364119db3fb7c'
        licencePlate = 'AA1111'
        self.service = '507'
        self.machineId = self.test.askForMachineId(licencePlate)
        self.token = self.test.getInBusWithMachineId(self.phoneId, self.service, self.machineId)

    def test_userReportsBusEventAndGetListUser(self):
        ''' user reports bus event and get list users '''

        user = self.test.createTranSappUsers(1)[0]
        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.service, self.eventCode, user.userId, user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(len(event['confirmedVoteList']), 1)
            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                               self.service, self.eventCode, 'confirm', user.userId,
                                                               user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(len(event['confirmedVoteList']), 2)
            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                               self.service, self.eventCode, 'decline', user.userId,
                                                               user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(len(event['confirmedVoteList']), 2)
            self.assertEqual(len(event['declinedVoteList']), 1)

    def test_userReportsStopEventAndGetListUser(self):
        ''' user reports bus event and get list users '''

        eventCode = 'evn00010'
        stopCode = 'PA433'
        self.test.insertBusstopsOnDatabase([stopCode])
        ScoreEvent.objects.create(code=eventCode, score=100)

        user = self.test.createTranSappUsers(1)[0]
        jsonResponse = self.test.reportStopEventByPost(self.phoneId, stopCode,
                                                       eventCode, user.userId, user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(len(event['confirmedVoteList']), 1)
            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineStopEventByPost(self.phoneId,
                                                                 stopCode, eventCode, 'confirm', user.userId,
                                                                 user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(len(event['confirmedVoteList']), 2)
            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineStopEventByPost(self.phoneId,
                                                                 stopCode, eventCode, 'decline', user.userId,
                                                                 user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(len(event['confirmedVoteList']), 2)
            self.assertEqual(len(event['declinedVoteList']), 1)
