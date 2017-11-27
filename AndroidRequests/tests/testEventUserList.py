from django.test import TransactionTestCase

from AndroidRequests.models import Level, ScoreEvent, EventRegistration
from AndroidRequests.tests.testHelper import TestHelper


class BusEventUserListTestCase(TransactionTestCase):
    """ test for user list returned by an event """
    fixtures = ["events"]

    def setUp(self):
        """ this method will automatically call for every single test """
        # create events
        self.test = TestHelper(self)
        self.eventCode = 'evn00201'

        # create levels 
        self.level = Level.objects.create(name='level 1', minScore=0, maxScore=1000, position=1)

        # create score event for eventCode
        self.score = 100
        ScoreEvent.objects.create(code=self.eventCode, score=self.score)

        self.phone_id = '1df6e1b6a1b840d689b364119db3fb7c'
        license_plate = 'AA1111'
        self.route = '507'
        self.machineId = self.test.askForMachineId(license_plate)
        self.token = self.test.getInBusWithMachineId(self.phone_id, self.route, self.machineId)

    def check_user_data(self, user, vote_number):
        """ check if user info is correct """
        self.assertEqual(user['votes'], vote_number)
        self.assertIn("id", user.keys())
        self.assertTrue(user['lastReportTimestamp'])

    def test_userReportsBusEventAndGetListUser(self):
        """ user reports bus event and get list users """

        user = self.test.createTranSappUsers(1)[0]
        json_response = self.test.reportEventV2ByPost(self.phone_id, self.machineId,
                                                      self.route, self.eventCode, user.userId, user.sessionToken)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 1)
            self.assertEqual(len(event['declinedVoteList']), 0)

        json_response = self.test.confirmOrDeclineEventV2ByPost(self.phone_id, self.machineId,
                                                                self.route, self.eventCode, EventRegistration.CONFIRM,
                                                                user.userId,
                                                                user.sessionToken)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)

            self.assertEqual(len(event['declinedVoteList']), 0)

        json_response = self.test.confirmOrDeclineEventV2ByPost(self.phone_id, self.machineId,
                                                                self.route, self.eventCode, EventRegistration.DECLINE,
                                                                user.userId,
                                                                user.sessionToken)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)
            self.assertEqual(len(event['declinedVoteList']), 1)
            for declinedUser in event['declinedVoteList']:
                self.check_user_data(declinedUser, 1)

    def test_userReportsStopEventAndGetListUser(self):
        """ user reports bus event and get list users """

        event_code = 'evn00010'
        stop_code = 'PA433'
        self.test.insertBusstopsOnDatabase([stop_code])
        ScoreEvent.objects.create(code=event_code, score=100)

        user = self.test.createTranSappUsers(1)[0]
        json_response = self.test.reportStopEventByPost(self.phone_id, stop_code,
                                                        event_code, user.userId, user.sessionToken)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 1)
            self.assertEqual(len(event['declinedVoteList']), 0)

        json_response = self.test.confirmOrDeclineStopEventByPost(self.phone_id,
                                                                  stop_code, event_code, EventRegistration.CONFIRM,
                                                                  user.userId,
                                                                  user.sessionToken)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)
            self.assertEqual(len(event['declinedVoteList']), 0)

        json_response = self.test.confirmOrDeclineStopEventByPost(self.phone_id,
                                                                  stop_code, event_code, EventRegistration.DECLINE,
                                                                  user.userId,
                                                                  user.sessionToken)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], 0)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 2)
            self.assertEqual(len(event['declinedVoteList']), 1)
            for declinedUser in event['declinedVoteList']:
                self.check_user_data(declinedUser, 1)

    def test_anonReportsStopEventAndAfterLoggedUserConfirmTheSameEvent(self):
        """ anon user reports stop event, after logged user confirm the same event.It checks that creator index = -1 """

        event_code = 'evn00010'
        stop_code = 'PA433'
        self.test.insertBusstopsOnDatabase([stop_code])
        ScoreEvent.objects.create(code=event_code, score=100)

        # anon event
        json_response = self.test.reportStopEventByPost(self.phone_id, stop_code,
                                                        event_code, None, None)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], -1)
            self.assertEqual(len(event['confirmedVoteList']), 0)
            self.assertEqual(len(event['declinedVoteList']), 0)

        # user event
        user = self.test.createTranSappUsers(1)[0]
        json_response = self.test.reportStopEventByPost(self.phone_id, stop_code,
                                                        event_code, user.userId, user.sessionToken)

        for event in json_response['events']:
            self.assertEqual(event['creatorIndex'], -1)
            self.assertEqual(len(event['confirmedVoteList']), 1)
            for confirmedUser in event['confirmedVoteList']:
                self.check_user_data(confirmedUser, 1)
            self.assertEqual(len(event['declinedVoteList']), 0)
