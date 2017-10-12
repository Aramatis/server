from django.test import TransactionTestCase

from AndroidRequests.models import Level, ScoreEvent, EventRegistration
from AndroidRequests.tests.testHelper import TestHelper


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
        licensePlate = 'AA1111'
        self.route = '507'
        self.machineId = self.test.askForMachineId(licensePlate)
        self.token = self.test.getInBusWithMachineId(self.phoneId, self.route, self.machineId)

    def check_user_data(self, user, vote_number):
        """ check if user info is correct """
        self.assertEqual(user['votes'], vote_number)
        self.assertIn("id", user.keys())
        #self.assertRaises(KeyError, user.__getitem__, 'id')
        self.assertTrue(user['lastReportTimestamp'])

    def test_userReportsBusEventAndGetListUser(self):
        """ user reports bus event and get list users """

        user = self.test.createTranSappUsers(1)[0]
        jsonResponse = self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                                     self.route, self.eventCode, user.userId, user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 1)
            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                               self.route, self.eventCode, EventRegistration.CONFIRM,
                                                               user.userId,
                                                               user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)

            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                               self.route, self.eventCode, EventRegistration.DECLINE,
                                                               user.userId,
                                                               user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)
            self.assertEqual(len(event['declinedVoteList']), 1)
            for declinedUser in event['declinedVoteList']:
                self.check_user_data(declinedUser, 1)

    def test_userReportsStopEventAndGetListUser(self):
        """ user reports bus event and get list users """

        eventCode = 'evn00010'
        stopCode = 'PA433'
        self.test.insertBusstopsOnDatabase([stopCode])
        ScoreEvent.objects.create(code=eventCode, score=100)

        user = self.test.createTranSappUsers(1)[0]
        jsonResponse = self.test.reportStopEventByPost(self.phoneId, stopCode,
                                                       eventCode, user.userId, user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 1)
            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineStopEventByPost(self.phoneId,
                                                                 stopCode, eventCode, EventRegistration.CONFIRM,
                                                                 user.userId,
                                                                 user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)
            self.assertEqual(len(event['declinedVoteList']), 0)

        jsonResponse = self.test.confirmOrDeclineStopEventByPost(self.phoneId,
                                                                 stopCode, eventCode, EventRegistration.DECLINE,
                                                                 user.userId,
                                                                 user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)
            self.assertEqual(len(event['declinedVoteList']), 1)
            for declinedUser in event['declinedVoteList']:
                self.check_user_data(declinedUser, 1)

    def test_anonReportsStopEventAndAfterLoggedUserConfirmTheSameEvent(self):
        """ anon user reports stop event, after logged user confirm the same event.It checks that creator index = -1 """

        eventCode = 'evn00010'
        stopCode = 'PA433'
        self.test.insertBusstopsOnDatabase([stopCode])
        ScoreEvent.objects.create(code=eventCode, score=100)

        # anon event
        jsonResponse = self.test.reportStopEventByPost(self.phoneId, stopCode,
                                                       eventCode, None, None)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], -1)
            self.assertEqual(len(event['confirmedVoteList']), 0)
            self.assertEqual(len(event['declinedVoteList']), 0)

        # user event
        user = self.test.createTranSappUsers(1)[0]
        jsonResponse = self.test.reportStopEventByPost(self.phoneId, stopCode,
                                                       eventCode, user.userId, user.sessionToken)

        for event in jsonResponse['events']:
            self.assertEqual(event['creatorIndex'], -1)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 1)
            self.assertEqual(len(event['declinedVoteList']), 0)
