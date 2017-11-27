from __future__ import unicode_literals
from django.test import TestCase

from AndroidRequests.statusResponse import Status
from AndroidRequests.tests.testHelper import TestHelper
from AndroidRequests.models import Token, ScoreHistory, ScoreEvent


class EvaluateTripTest(TestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.test = TestHelper(self)

        self.service = '401'
        self.license_plate = 'AA1111'
        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.test.insertServicesOnDatabase([self.service])

        self.token = self.test.getInBusWithLicencePlateByPost(
            self.phone_id, self.service, self.license_plate)

    def test_tripEvaluationWithGoodEvaluationFormat(self):
        """This method test trip evaluation """

        evaluation = 1
        json_response = self.test.evaluateTrip(self.token, evaluation)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_response['message'], Status.getJsonStatus(Status.OK, {})['message'])
        self.assertEqual(Token.objects.get(token=self.token).userEvaluation, evaluation)

    def test_tripEvaluationWithBadEvaluationFormat(self):
        """This method test trip evaluation """

        evaluation = "asd"
        json_response = self.test.evaluateTrip(self.token, evaluation)

        self.assertEqual(json_response['status'], Status.getJsonStatus(
            Status.TRIP_EVALUATION_FORMAT_ERROR, {})['status'])
        self.assertEqual(json_response['message'], Status.getJsonStatus(
            Status.TRIP_EVALUATION_FORMAT_ERROR, {})['message'])
        self.assertEqual(Token.objects.get(token=self.token).userEvaluation, None)

    def test_tripEvaluationWithWrongToken(self):
        """This method test trip evaluation """

        evaluation = 5
        json_response = self.test.evaluateTrip('aasd', evaluation)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['status'])
        self.assertEqual(json_response['message'],
                         Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['message'])
        self.assertEqual(Token.objects.get(token=self.token).userEvaluation, None)


class EvaluateTripWithLoggedUserTest(TestCase):
    """ test for DevicePositionInTime model """
    fixtures = ["scoreEvents"]

    def setUp(self):
        """ this method will automatically call for every single test """

        self.test = TestHelper(self)

        self.service = '401'
        self.license_plate = 'AA1111'
        self.phone_id = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.test.insertServicesOnDatabase([self.service])

        self.transapp_user_obj = self.test.createTranSappUsers(1)[0]

        self.token = self.test.getInBusWithLicencePlateByPost(
            self.phone_id, self.service, self.license_plate, user_id=self.transapp_user_obj.userId,
            session_token=self.transapp_user_obj.sessionToken)

    def test_tripEvaluation(self):
        """ logged user evaluates trip, so we will give to him some points """

        evaluation = 1
        json_response = self.test.evaluateTrip(self.token, evaluation, self.transapp_user_obj.userId,
                                               self.transapp_user_obj.sessionToken)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(json_response['message'], Status.getJsonStatus(Status.OK, {})['message'])
        self.assertEqual(Token.objects.get(token=self.token).userEvaluation, evaluation)

        # check points
        self.assertEquals(ScoreHistory.objects.count(), 1)
        score_obj = ScoreHistory.objects.select_related("scoreEvent").first()
        evaluation_code = "evn00301"
        score_event_obj = ScoreEvent.objects.get(code=evaluation_code)
        self.assertEquals(score_obj.score, score_event_obj.score)
        self.assertIn(self.token, score_obj.meta)
        self.assertEquals(score_obj.scoreEvent, score_event_obj)
