from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

# my stuff
from AndroidRequests.models import DevicePositionInTime, Bus, BusStop, Service, ServiceStopDistance, ServiceLocation, ActiveToken, Token, EventForBusStop, Event, Busv2, Busassignment
# views
import AndroidRequests.views as views
from AndroidRequests.statusResponse import Status
from AndroidRequests.tests.testHelper import TestHelper

# Create your tests here.


class EvaluateTripTest(TestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.test = TestHelper(self)

        self.service = '401'
        self.licencePlate = 'AA1111'
        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        self.test.insertServicesOnDatabase([self.service])

        self.token = self.test.getInBusWithLicencePlate(
                self.userId, self.service, self.licencePlate)

    def test_tripEvaluationWithGoodEvaluationFormat(self):
        '''This method test trip evaluation '''

        evaluation = 1
        jsonResponse = self.test.evaluateTrip(self.token, evaluation)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.OK, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.OK, {})['message'])
        self.assertEqual(Token.objects.get(token=self.token).userEvaluation, evaluation)

    def test_tripEvaluationWithBadEvaluationFormat(self):
        '''This method test trip evaluation '''

        evaluation = "asd"
        jsonResponse = self.test.evaluateTrip(self.token, evaluation)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.TRIP_EVALUATION_FORMAT_ERROR, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.TRIP_EVALUATION_FORMAT_ERROR, {})['message'])
        self.assertEqual(Token.objects.get(token=self.token).userEvaluation, None)

    def test_tripEvaluationWithWrongToken(self):
        '''This method test trip evaluation '''

        evaluation = 5
        jsonResponse = self.test.evaluateTrip('aasd', evaluation)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['status'])
        self.assertEqual(jsonResponse['message'], Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, {})['message'])
        self.assertEqual(Token.objects.get(token=self.token).userEvaluation, None)

