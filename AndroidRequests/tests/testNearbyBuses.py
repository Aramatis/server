from django.test import TransactionTestCase, TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
import json

# my stuff
from AndroidRequests.tests.testHelper import TestHelper
# views
import AndroidRequests.views as views
import AndroidRequests.constants as Constants


class NearbyBusesTest(TestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.phoneId2 = "971087e3-b64c-4c22-88c2-2e1300ffd855"

        self.helper = TestHelper(self)

        self.service = '507'
        self.busStop = 'PA459'

        self.helper.insertServicesOnDatabase([self.service])
        self.helper.insertBusstopsOnDatabase([self.busStop])
        self.helper.insertServicesByBusstopsOnDatabase([self.busStop])
        self.helper.insertServiceStopDistanceOnDatabase([self.busStop])
        self.helper.insertServiceLocationOnDatabase([self.service + 'R'])

    def test_nearbyBuses(self):

        factory = RequestFactory()
        request = factory.get('/android/nearbyBuses')
        request.user = AnonymousUser()

        response = views.nearbyBuses(request, self.phoneId, self.busStop)

        self.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        if (jsonResponse['DTPMError'] != ""):
            self.assertEqual(jsonResponse['DTPMError'],
                    "You do not have permission to do this! >:(.")
        else:
            self.assertEqual('servicios' in jsonResponse, True)
            self.assertEqual('eventos' in jsonResponse, True)

class NearbyBusesResponseTest(TestCase):
    """ test for response of nearbybuses function """

    def setUp(self):
        """ this method will automatically call for every single test """

        self.phoneId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.phoneId2 = "971087e3-b64c-4c22-88c2-2e1300ffd855"

        self.helper = TestHelper(self)

        self.direction = 'I'
        self.stopCode = 'PA433'
        self.service = '507'
        self.helper.insertBusstopsOnDatabase([self.stopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509', '507'])
        self.helper.insertServicesByBusstopsOnDatabase([self.stopCode])
        self.helper.insertServiceStopDistanceOnDatabase([self.stopCode])
        self.helper.insertServiceLocationOnDatabase(['506I', '506eI', '506vI', '509I', '507I'])

    def getBuses(self, stopCode, phoneId, indexPairList):
        ''' generate nearbybuses response '''

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(stopCode, phoneId)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        # authBuses return 9 of 10 buses because one of them does not have license plate
        buses = views.mergeBuses(userBuses, authBuses)

        for busIndex, authIndexAnswer in indexPairList:
            self.assertEqual(
                buses[busIndex]['patente'],
                fakeJsonAuthorityAnswer['servicios'][authIndexAnswer]['patente'])

        return buses

    def test_nearbyBusesWithFakeAuthorityInfoWithoutUserBuses(self):
        """ test methods used that uses nearbyBuses url. case: only authority buses """

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (0, 0), (1, 1), (2, 2), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
        buses = self.getBuses(self.stopCode, self.phoneId, indexPairList)

    def test_nearbyBusesWithFakeAuthorityInfoWithOneUserBus(self):
        """ test methods that uses nearbyBuses url. case: authority buses with one user bus"""

        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, self.direction)

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (1, 0), (2, 1), (3, 2), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
        buses = self.getBuses(self.stopCode, self.phoneId2, indexPairList)

        self.assertEqual(len(buses), 9 + 1)
        self.assertEqual(buses[0]['patente'], Constants.DUMMY_LICENSE_PLATE)
        self.assertEqual(buses[0]['servicio'], self.service)
        self.assertEqual(buses[0]['direction'], self.direction)

    def test_nearbyBusesWithFakeAuthorityInfoWithTwoUserBus(self):
        """ test methods that uses nearbyBuses url. case: authority buses with two dummy user bus"""

        # first user
        travelKey1 = self.helper.getInBusWithLicencePlate(
            self.phoneId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey1)
        self.helper.setDirection(travelKey1, self.direction)

        # second user
        direction2 = "I"
        travelKey2 = self.helper.getInBusWithLicencePlate(
            self.phoneId2, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey2)
        self.helper.setDirection(travelKey2, direction2)

        # user who ask for stop info
        otherUser = '0cf16966-8643-4887-92b4-7015b4d1dbde'

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (2, 0), (3, 1), (4, 2), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9)]
        buses = self.getBuses(self.stopCode, otherUser, indexPairList)

        self.assertEqual(len(buses), 9 + 1 + 1)
        self.assertEqual(buses[0]['patente'], Constants.DUMMY_LICENSE_PLATE)
        self.assertEqual(buses[0]['servicio'], self.service)
        self.assertEqual(buses[0]['direction'], self.direction)
        self.assertEqual(buses[1]['patente'], Constants.DUMMY_LICENSE_PLATE)
        self.assertEqual(buses[1]['servicio'], self.service)
        self.assertEqual(buses[1]['direction'], direction2)

    def test_nearbyBusesWithFakeAuthorityInfoWithTwoUserInTheSameBus(self):
        """ test methods that uses nearbyBuses url. case: authority buses with two user in the same bus. 
            The bus comes in the authority bus list """

        direction2 = 'I'
        licencePlate = 'bjfb28'
        service = '506'
        # first user get in the bus
        travelKey1 = self.helper.getInBusWithLicencePlate(
            self.phoneId, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey1)
        self.helper.setDirection(travelKey1, self.direction)
        # second user get in the same bus 
        travelKey2 = self.helper.getInBusWithLicencePlate(
            self.phoneId2, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey2)
        self.helper.setDirection(travelKey2, direction2)

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (0, 0), (1, 1), (2, 2), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
        buses = self.getBuses(self.stopCode, self.phoneId2, indexPairList)

        self.assertEqual(len(buses), 9)
        # this is the fake bus
        self.assertEqual(buses[0]['patente'], licencePlate.upper())
        self.assertEqual(buses[0]['servicio'], service)
        self.assertEqual(buses[0]['tienePasajeros'], 2)
        self.assertEqual(buses[0]['distanciaMts'], 1691)
        self.assertEqual(buses[0]['tiempoV2'], "0 a 5 min")
        self.assertEqual(buses[0]['distanciaV2'], "1.69Km")
        self.assertEqual(buses[0]['direction'], "I")

    def test_nearbyBusesWithFakeAuthorityInfoWithUserBusThatMatchWithAuthorityBus(
            self):
        """ test methods that uses nearbyBuses url. case: authority buses with user bus that match with authority bus """
        licencePlate = 'bjFb28'
        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, self.direction)

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (1, 1), (2, 2), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
        buses = self.getBuses(self.stopCode, self.phoneId2, indexPairList)

        self.assertEqual(len(buses), 9)
        self.assertEqual(buses[0]['patente'], licencePlate.upper())
        self.assertEqual(buses[0]['servicio'], service)
        self.assertEqual(buses[0]['tienePasajeros'], 1)
        self.assertEqual(buses[0]['direction'], self.direction)

    def test_nearbyBusesWithFakeAuthorityInfoWithUserBusWithoutDirection(self):
        """ test methods that uses nearbyBuses url. case: authority buses with user bus without direction, so the user bus should not see in the list of buses """

        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (0, 0), (1, 1), (2, 2), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
        buses = self.getBuses(self.stopCode, self.phoneId2, indexPairList)

        self.assertEqual(len(buses), 9)

    def test_nearbyBusesWhenUserIsOnTheBus(self):
        """ test methods that uses nearbyBuses url.
        case: ask for buses when the user is in one of bus that goes to the bus stop asked """

        licencePlate = 'bjFb28'
        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, self.direction)

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (0, 1), (1, 2), (2, 4), (3, 5), (4, 6), (5, 7), (6, 8), (7, 9)]
        buses = self.getBuses(self.stopCode, self.phoneId, indexPairList)

        self.assertEqual(len(buses), 8)

    def test_nearbyBusesWhenUserIsOnTheDummyBus(self):
        """ test methods that uses nearbyBuses url.
        case: ask for buses when the user is in one of bus that stops in the bus stop asked """

        # licencePlate = 'bjFb28'
        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.phoneId, service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, self.direction)

        # to compare response given by nearbybuses function and authority (in that order)
        indexPairList = [
                (0, 0), (1, 1), (2, 2), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
        buses = self.getBuses(self.stopCode, self.phoneId, indexPairList)

        self.assertEqual(len(buses), 9)


class FormattersTest(TestCase):
    """ test for formatters used vi nearbybuses function """

    def setUp(self):
        """ this method will automatically call for every single test """

    def test_FormatDistance(self):
        """ test method that apply distance format  """
        distanceLessThan1000 = 585
        distanceGreaterThan1000NotInt = 1856
        distanceGreaterThan1000Int = 2000

        self.assertEqual(views.formatDistance(distanceLessThan1000), "585m")
        self.assertEqual(views.formatDistance(
            distanceGreaterThan1000NotInt), "1.86Km")
        self.assertEqual(views.formatDistance(
            distanceGreaterThan1000Int), "2Km")

    def test_FormatServiceName(self):
        """ test method that apply service format to service names """
        serviceName1 = "506E"
        serviceName2 = "506N"
        serviceName3 = "D03N"
        serviceName4 = "D03E"
        serviceName5 = "D03"
        serviceName6 = "N50"
        serviceName7 = "506"

        self.assertEqual(views.formatServiceName(serviceName1), "506e")
        self.assertEqual(views.formatServiceName(serviceName2), "506N")
        self.assertEqual(views.formatServiceName(serviceName3), "D03N")
        self.assertEqual(views.formatServiceName(serviceName4), "D03e")
        self.assertEqual(views.formatServiceName(serviceName5), "D03")
        self.assertEqual(views.formatServiceName(serviceName6), "N50")
        self.assertEqual(views.formatServiceName(serviceName7), "506")

    def test_FormatTime(self):
        """ test method that apply time format """

        times = [
            "Menos de 5 min.",
            "Entre 19 Y 29 min.",
            "Mas de 45 min.",
            "En menos de 10 min.",
            "Otro caso"]
        distances = [50, 150]

        answers = [
            "Llegando",
            "0 a 5 min",
            "19 a 29 min",
            "19 a 29 min",
            "+ de 45 min",
            "+ de 45 min",
            "Llegando",
            "0 a 10 min",
            "Otro caso",
            "Otro caso"]
        index = 0
        for time in times:
            for distance in distances:
                self.assertEqual(
                    views.formatTime(
                        time,
                        distance),
                    answers[index])
                index += 1
