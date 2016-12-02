from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
import json

# my stuff
from AndroidRequests.tests.testHelper import TestHelper
# views
import AndroidRequests.views as views
import AndroidRequests.constants as Constants


class NearbyBusTest(TestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """
        # for testing requests inside the project
        self.factory = RequestFactory()

        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"
        self.userId2 = "971087e3-b64c-4c22-88c2-2e1300ffd855"

        self.helper = TestHelper(self)

        self.service = '507'
        self.busStop = 'PA459'

        self.helper.insertServicesOnDatabase([self.service])
        self.helper.insertBusstopsOnDatabase([self.busStop])
        self.helper.insertServicesByBusstopsOnDatabase([self.busStop])

    def test_nearbyBuses(self):
        request = self.factory.get('/android/nearbyBuses')
        request.user = AnonymousUser()

        busStopCodeThis = 'PA459'
        self.helper.insertServicesByBusstopsOnDatabase([busStopCodeThis])

        response = views.nearbyBuses(request, self.userId, busStopCodeThis)

        self.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        if (jsonResponse['DTPMError'] != ""):
            self.assertEqual(jsonResponse['DTPMError'],
                             "Usted no cuenta con los permisos necesarios para realizar esta consulta.")
        else:
            self.assertEqual('servicios' in jsonResponse, True)
            self.assertEqual('eventos' in jsonResponse, True)

    def test_nearbyBusesWithFakeAuthorityInfoWithoutUserBuses(self):
        """ test methods used that uses nearbyBuses url. case: only authority buses """

        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        busStopCode = 'PA433'
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        # TODO: FALTA TOMAR UNA URL REAL Y LA FORMATEADA
        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(busStopCode, self.userId2)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)

        buses = views.mergeBuses(userBuses, authBuses)

        jsonUrlAnswer = json.loads('{"eventos": [], "servicios": [{"servicio": "506", "eventos": [], "tiempo": "Menos de 5 min.", "random": false, "busId": "417d8ef0-aaac-4c91-b9c2-3835060ece89", "distancia": "1691  mts.", "patente": "BJFB28", "valido": 1, "lon": -70.6817326, "distanciaV2": "1.69Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "0 a 5 min", "lat": -33.45898995, "direction": "I", "sentido": "right", "distanciaMts": 1691}, {"servicio": "506", "eventos": [], "tiempo": "Entre 03 Y 07 min. ", "random": false, "busId": "e86d3567-3a5d-48d3-b4a4-f0a139ab3825", "distancia": "1921  mts.", "patente": "BJFC56", "valido": 1, "lon": -70.68422918, "distanciaV2": "1.92Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "03 a 07 min", "lat": -33.45909322, "direction": "I", "sentido": "right", "distanciaMts": 1921}, {"servicio": "506e", "eventos": [], "tiempo": "Menos de 5 min.", "random": false, "busId": "2c88087e-1c8d-4c47-9ccc-f4a28a25dba3", "distancia": "771  mts.", "patente": "BJFH28", "valido": 1, "lon": -70.67206943, "distanciaV2": "771m", "color": 7, "tienePasajeros": 0, "tiempoV2": "0 a 5 min", "lat": -33.45841956, "direction": "I", "sentido": "right", "distanciaMts": 771}, {"servicio": "506v", "eventos": [], "tiempo": "Menos de 5 min.", "random": false, "busId": "9db62e10-37a7-4cc4-8ee8-d66718e3d9f2", "distancia": "1922  mts.", "patente": "FDJX64", "valido": 1, "lon": -70.68417605, "distanciaV2": "1.92Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "0 a 5 min", "lat": -33.45909223, "direction": "I", "sentido": "right", "distanciaMts": 1922}, {"servicio": "506v", "eventos": [], "tiempo": "Entre 04 Y 08 min. ", "random": false, "busId": "33c58d9e-355c-42db-9962-48150f17bb91", "distancia": "1572  mts.", "patente": "BFKB96", "valido": 1, "lon": -70.68060597, "distanciaV2": "1.57Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "04 a 08 min", "lat": -33.4589299, "direction": "I", "sentido": "right", "distanciaMts": 1572}, {"servicio": "507", "eventos": [], "tiempo": "Entre 11 Y 17 min. ", "random": false, "busId": "7978130a-1458-4415-8224-4b9e2a645da2", "distancia": "3194  mts.", "patente": "BJFH27", "valido": 1, "lon": -70.67964937, "distanciaV2": "3.19Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "11 a 17 min", "lat": -33.44337385, "direction": "I", "sentido": "right", "distanciaMts": 3194}, {"servicio": "507", "eventos": [], "tiempo": "Entre 20 Y 30 min. ", "random": false, "busId": "710b2e84-bc2c-44bc-829f-dbb07af0efb0", "distancia": "6094  mts.", "patente": "BJFC20", "valido": 1, "lon": -70.69886029, "distanciaV2": "6.09Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "20 a 30 min", "lat": -33.4318278, "direction": "I", "sentido": "right", "distanciaMts": 6094}, {"servicio": "509", "eventos": [], "tiempo": "Entre 04 Y 08 min. ", "random": false, "busId": "84a6dcf9-d69a-4ca2-8e83-8f996711a31f", "distancia": "1953  mts.", "patente": "FLXC45", "valido": 1, "lon": -70.68453181, "distanciaV2": "1.95Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "04 a 08 min", "lat": -33.45909886, "direction": "I", "sentido": "right", "distanciaMts": 1953}, {"servicio": "509", "eventos": [], "tiempo": "Entre 08 Y 14 min. ", "random": false, "busId": "1c5104a7-ae01-485c-9687-533d46ad965f", "distancia": "3273  mts.", "patente": "FLXD43", "valido": 1, "lon": -70.69789113, "distanciaV2": "3.27Km", "color": 7, "tienePasajeros": 0, "tiempoV2": "08 a 14 min", "lat": -33.46160623, "direction": "I", "sentido": "right", "distanciaMts": 3273}], "DTPMError": ""}')['servicios']

        self.assertEqual(buses[0]['patente'], jsonUrlAnswer[0]['patente'])
        self.assertEqual(buses[1]['patente'], jsonUrlAnswer[1]['patente'])
        self.assertEqual(buses[2]['patente'], jsonUrlAnswer[2]['patente'])
        self.assertEqual(buses[3]['patente'], jsonUrlAnswer[3]['patente'])
        self.assertEqual(buses[4]['patente'], jsonUrlAnswer[4]['patente'])
        self.assertEqual(buses[5]['patente'], jsonUrlAnswer[5]['patente'])
        self.assertEqual(buses[6]['patente'], jsonUrlAnswer[6]['patente'])
        self.assertEqual(buses[7]['patente'], jsonUrlAnswer[7]['patente'])
        self.assertEqual(buses[8]['patente'], jsonUrlAnswer[8]['patente'])

    def test_nearbyBusesWithFakeAuthorityInfoWithOneUserBus(self):
        """ test methods that uses nearbyBuses url. case: authority buses with one user bus"""

        direction = "I"
        busStopCode = 'PA433'
        self.helper.insertBusstopsOnDatabase([busStopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        travelKey = self.helper.getInBusWithLicencePlate(
            self.userId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, direction)

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(busStopCode, self.userId2)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        buses = views.mergeBuses(userBuses, authBuses)

        self.assertEqual(len(buses), 9 + 1)
        self.assertEqual(buses[0]['patente'], Constants.DUMMY_LICENSE_PLATE)
        self.assertEqual(buses[0]['servicio'], self.service)
        self.assertEqual(buses[0]['direction'], direction)
        self.assertEqual(
            buses[1]['patente'],
            fakeJsonAuthorityAnswer['servicios'][0]['patente'])
        self.assertEqual(
            buses[2]['patente'],
            fakeJsonAuthorityAnswer['servicios'][1]['patente'])
        self.assertEqual(
            buses[3]['patente'],
            fakeJsonAuthorityAnswer['servicios'][2]['patente'])
        self.assertEqual(
            buses[4]['patente'],
            fakeJsonAuthorityAnswer['servicios'][4]['patente'])
        self.assertEqual(
            buses[5]['patente'],
            fakeJsonAuthorityAnswer['servicios'][5]['patente'])
        self.assertEqual(
            buses[6]['patente'],
            fakeJsonAuthorityAnswer['servicios'][6]['patente'])
        self.assertEqual(
            buses[7]['patente'],
            fakeJsonAuthorityAnswer['servicios'][7]['patente'])
        self.assertEqual(
            buses[8]['patente'],
            fakeJsonAuthorityAnswer['servicios'][8]['patente'])
        self.assertEqual(
            buses[9]['patente'],
            fakeJsonAuthorityAnswer['servicios'][9]['patente'])

    def test_nearbyBusesWithFakeAuthorityInfoWithTwoUserBus(self):
        """ test methods that uses nearbyBuses url. case: authority buses with two dummy user bus"""

        busStopCode = 'PA433'
        self.helper.insertBusstopsOnDatabase([busStopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        # first user
        direction1 = "I"
        travelKey1 = self.helper.getInBusWithLicencePlate(
            self.userId, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey1)
        self.helper.setDirection(travelKey1, direction1)
        # second user
        userId2 = 'ce102dcd-0670-4086-a543-b3e6e58e8f58'
        direction2 = "I"
        travelKey2 = self.helper.getInBusWithLicencePlate(
            userId2, self.service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey2)
        self.helper.setDirection(travelKey2, direction2)

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(busStopCode, self.userId2)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        buses = views.mergeBuses(userBuses, authBuses)

        self.assertEqual(len(buses), 9 + 1 + 1)
        self.assertEqual(buses[0]['patente'], Constants.DUMMY_LICENSE_PLATE)
        self.assertEqual(buses[0]['servicio'], self.service)
        self.assertEqual(buses[0]['direction'], direction1)
        self.assertEqual(buses[1]['patente'], Constants.DUMMY_LICENSE_PLATE)
        self.assertEqual(buses[1]['servicio'], self.service)
        self.assertEqual(buses[1]['direction'], direction2)
        self.assertEqual(
            buses[2]['patente'],
            fakeJsonAuthorityAnswer['servicios'][0]['patente'])
        self.assertEqual(
            buses[3]['patente'],
            fakeJsonAuthorityAnswer['servicios'][1]['patente'])
        self.assertEqual(
            buses[4]['patente'],
            fakeJsonAuthorityAnswer['servicios'][2]['patente'])
        self.assertEqual(
            buses[5]['patente'],
            fakeJsonAuthorityAnswer['servicios'][4]['patente'])
        self.assertEqual(
            buses[6]['patente'],
            fakeJsonAuthorityAnswer['servicios'][5]['patente'])
        self.assertEqual(
            buses[7]['patente'],
            fakeJsonAuthorityAnswer['servicios'][6]['patente'])
        self.assertEqual(
            buses[8]['patente'],
            fakeJsonAuthorityAnswer['servicios'][7]['patente'])
        self.assertEqual(
            buses[9]['patente'],
            fakeJsonAuthorityAnswer['servicios'][8]['patente'])
        self.assertEqual(
            buses[10]['patente'],
            fakeJsonAuthorityAnswer['servicios'][9]['patente'])

    def test_nearbyBusesWithFakeAuthorityInfoWithTwoUserInTheSameBus(self):
        """ test methods that uses nearbyBuses url. case: authority buses with two user in the same bus"""

        direction1 = "I"
        direction2 = "I"
        busStopCode = 'PA433'
        self.helper.insertBusstopsOnDatabase([busStopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        licencePlate = 'bjfb28'
        service = '506'
        # first user
        travelKey1 = self.helper.getInBusWithLicencePlate(
            self.userId, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey1)
        self.helper.setDirection(travelKey1, direction1)
        # second user
        userId2 = 'ce102dcd-0670-4086-a543-b3e6e58e8f58'
        travelKey2 = self.helper.getInBusWithLicencePlate(
            userId2, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey2)
        self.helper.setDirection(travelKey2, direction2)

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)
        userBuses = views.getUserBuses(busStopCode, self.userId2)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        buses = views.mergeBuses(userBuses, authBuses)
        self.assertEqual(len(buses), 9)
        self.assertEqual(buses[0]['patente'], licencePlate.upper())
        self.assertEqual(buses[0]['servicio'], service)
        self.assertEqual(buses[0]['tienePasajeros'], 2)
        self.assertEqual(buses[0]['distanciaMts'], 1691)
        self.assertEqual(buses[0]['tiempoV2'], "0 a 5 min")
        self.assertEqual(buses[0]['distanciaV2'], "1.69Km")
        self.assertEqual(buses[0]['direction'], "I")
        self.assertEqual(
            buses[1]['patente'],
            fakeJsonAuthorityAnswer['servicios'][1]['patente'])
        self.assertEqual(
            buses[2]['patente'],
            fakeJsonAuthorityAnswer['servicios'][2]['patente'])
        self.assertEqual(
            buses[3]['patente'],
            fakeJsonAuthorityAnswer['servicios'][4]['patente'])
        self.assertEqual(
            buses[4]['patente'],
            fakeJsonAuthorityAnswer['servicios'][5]['patente'])
        self.assertEqual(
            buses[5]['patente'],
            fakeJsonAuthorityAnswer['servicios'][6]['patente'])
        self.assertEqual(
            buses[6]['patente'],
            fakeJsonAuthorityAnswer['servicios'][7]['patente'])
        self.assertEqual(
            buses[7]['patente'],
            fakeJsonAuthorityAnswer['servicios'][8]['patente'])
        self.assertEqual(
            buses[8]['patente'],
            fakeJsonAuthorityAnswer['servicios'][9]['patente'])

    def test_nearbyBusesWithFakeAuthorityInfoWithUserBusThatMatchWithAuthorityBus(
            self):
        """ test methods that uses nearbyBuses url. case: authority buses with user bus that match with authority bus """

        busStopCode = 'PA433'
        self.helper.insertBusstopsOnDatabase([busStopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        direction = "I"
        licencePlate = 'bjFb28'
        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.userId, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, direction)

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(busStopCode, self.userId2)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        buses = views.mergeBuses(userBuses, authBuses)

        self.assertEqual(len(buses), 9)
        self.assertEqual(buses[0]['patente'], licencePlate.upper())
        self.assertEqual(buses[0]['servicio'], service)
        self.assertEqual(buses[0]['tienePasajeros'], 1)
        self.assertEqual(buses[0]['direction'], direction)
        self.assertEqual(
            buses[1]['patente'],
            fakeJsonAuthorityAnswer['servicios'][1]['patente'])
        self.assertEqual(
            buses[2]['patente'],
            fakeJsonAuthorityAnswer['servicios'][2]['patente'])
        self.assertEqual(
            buses[3]['patente'],
            fakeJsonAuthorityAnswer['servicios'][4]['patente'])
        self.assertEqual(
            buses[4]['patente'],
            fakeJsonAuthorityAnswer['servicios'][5]['patente'])
        self.assertEqual(
            buses[5]['patente'],
            fakeJsonAuthorityAnswer['servicios'][6]['patente'])
        self.assertEqual(
            buses[6]['patente'],
            fakeJsonAuthorityAnswer['servicios'][7]['patente'])
        self.assertEqual(
            buses[7]['patente'],
            fakeJsonAuthorityAnswer['servicios'][8]['patente'])
        self.assertEqual(
            buses[8]['patente'],
            fakeJsonAuthorityAnswer['servicios'][9]['patente'])

    def test_nearbyBusesWithFakeAuthorityInfoWithUserBusWithoutDirection(self):
        """ test methods that uses nearbyBuses url. case: authority buses with user bus without direction, so the user bus should not see in the list of buses """

        busStopCode = 'PA433'
        self.helper.insertBusstopsOnDatabase([busStopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        # licencePlate = 'bjFb28'
        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.userId, service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        # self.helper.setDirection(travelKey, direction)

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(busStopCode, self.userId2)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        buses = views.mergeBuses(userBuses, authBuses)

        self.assertEqual(len(buses), 9)
        self.assertEqual(
            buses[0]['patente'],
            fakeJsonAuthorityAnswer['servicios'][0]['patente'])
        self.assertEqual(
            buses[1]['patente'],
            fakeJsonAuthorityAnswer['servicios'][1]['patente'])
        self.assertEqual(
            buses[2]['patente'],
            fakeJsonAuthorityAnswer['servicios'][2]['patente'])
        self.assertEqual(
            buses[3]['patente'],
            fakeJsonAuthorityAnswer['servicios'][4]['patente'])
        self.assertEqual(
            buses[4]['patente'],
            fakeJsonAuthorityAnswer['servicios'][5]['patente'])
        self.assertEqual(
            buses[5]['patente'],
            fakeJsonAuthorityAnswer['servicios'][6]['patente'])
        self.assertEqual(
            buses[6]['patente'],
            fakeJsonAuthorityAnswer['servicios'][7]['patente'])
        self.assertEqual(
            buses[7]['patente'],
            fakeJsonAuthorityAnswer['servicios'][8]['patente'])
        self.assertEqual(
            buses[8]['patente'],
            fakeJsonAuthorityAnswer['servicios'][9]['patente'])

    def test_nearbyBusesWhenUserIsOnTheBus(self):
        """ test methods that uses nearbyBuses url.
        case: ask for buses when the user is in one of bus that goes to the bus stop asked """

        busStopCode = 'PA433'
        self.helper.insertBusstopsOnDatabase([busStopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        direction = "I"
        licencePlate = 'bjFb28'
        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.userId, service, licencePlate)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, direction)

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(busStopCode, self.userId)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        buses = views.mergeBuses(userBuses, authBuses)

        self.assertEqual(len(buses), 8)
        self.assertEqual(
            buses[0]['patente'],
            fakeJsonAuthorityAnswer['servicios'][1]['patente'])
        self.assertEqual(
            buses[1]['patente'],
            fakeJsonAuthorityAnswer['servicios'][2]['patente'])
        self.assertEqual(
            buses[2]['patente'],
            fakeJsonAuthorityAnswer['servicios'][4]['patente'])
        self.assertEqual(
            buses[3]['patente'],
            fakeJsonAuthorityAnswer['servicios'][5]['patente'])
        self.assertEqual(
            buses[4]['patente'],
            fakeJsonAuthorityAnswer['servicios'][6]['patente'])
        self.assertEqual(
            buses[5]['patente'],
            fakeJsonAuthorityAnswer['servicios'][7]['patente'])
        self.assertEqual(
            buses[6]['patente'],
            fakeJsonAuthorityAnswer['servicios'][8]['patente'])
        self.assertEqual(
            buses[7]['patente'],
            fakeJsonAuthorityAnswer['servicios'][9]['patente'])

    def test_nearbyBusesWhenUserIsOnTheDummyBus(self):
        """ test methods that uses nearbyBuses url.
        case: ask for buses when the user is in one of bus that stops in the bus stop asked """

        busStopCode = 'PA433'
        self.helper.insertBusstopsOnDatabase([busStopCode])
        self.helper.insertServicesOnDatabase(['506', '506e', '506v', '509'])
        self.helper.insertServicesByBusstopsOnDatabase([busStopCode])

        direction = "I"
        # licencePlate = 'bjFb28'
        service = '506'
        travelKey = self.helper.getInBusWithLicencePlate(
            self.userId, service, Constants.DUMMY_LICENSE_PLATE)
        self.helper.sendFakeTrajectoryOfToken(travelKey)
        self.helper.setDirection(travelKey, direction)

        fakeAuthorityAnswer = '{"horaConsulta": "10:12", "servicios": [{"servicio": "506", "patente": "BJFB-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1691  mts."}, {"servicio": "506", "patente": "BJFC-56", "tiempo": "Entre 03 Y 07 min. ", "valido": 1, "distancia": "1921  mts."}, {"servicio": "506E", "patente": "BJFH-28", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "771  mts."}, {"servicio": "506E", "patente": null, "tiempo": null, "valido": 1, "distancia": "None  mts."}, {"servicio": "506V", "patente": "FDJX-64", "tiempo": "Menos de 5 min.", "valido": 1, "distancia": "1922  mts."}, {"servicio": "506V", "patente": "BFKB-96", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1572  mts."}, {"servicio": "507", "patente": "BJFH-27", "tiempo": "Entre 11 Y 17 min. ", "valido": 1, "distancia": "3194  mts."}, {"servicio": "507", "patente": "BJFC-20", "tiempo": "Entre 20 Y 30 min. ", "valido": 1, "distancia": "6094  mts."}, {"servicio": "509", "patente": "FLXC-45", "tiempo": "Entre 04 Y 08 min. ", "valido": 1, "distancia": "1953  mts."}, {"servicio": "509", "patente": "FLXD-43", "tiempo": "Entre 08 Y 14 min. ", "valido": 1, "distancia": "3273  mts."}], "webTransId": "TSPP00000000000000219461", "error": null, "descripcion": "PARADA 1 / ESCUELA   DE INGENIERIA", "fechaConsulta": "2016-11-02", "id": "PA433"}'

        fakeJsonAuthorityAnswer = json.loads(fakeAuthorityAnswer)

        userBuses = views.getUserBuses(busStopCode, self.userId)
        authBuses = views.getAuthorityBuses(fakeJsonAuthorityAnswer)
        buses = views.mergeBuses(userBuses, authBuses)

        self.assertEqual(len(buses), 9)
        self.assertEqual(
            buses[0]['patente'],
            fakeJsonAuthorityAnswer['servicios'][0]['patente'])
        self.assertEqual(
            buses[1]['patente'],
            fakeJsonAuthorityAnswer['servicios'][1]['patente'])
        self.assertEqual(
            buses[2]['patente'],
            fakeJsonAuthorityAnswer['servicios'][2]['patente'])
        self.assertEqual(
            buses[3]['patente'],
            fakeJsonAuthorityAnswer['servicios'][4]['patente'])
        self.assertEqual(
            buses[4]['patente'],
            fakeJsonAuthorityAnswer['servicios'][5]['patente'])
        self.assertEqual(
            buses[5]['patente'],
            fakeJsonAuthorityAnswer['servicios'][6]['patente'])
        self.assertEqual(
            buses[6]['patente'],
            fakeJsonAuthorityAnswer['servicios'][7]['patente'])
        self.assertEqual(
            buses[7]['patente'],
            fakeJsonAuthorityAnswer['servicios'][8]['patente'])

    def test_nearbyBusesFormatDistance(self):
        """ test method that apply distance format  """
        distanceLessThan1000 = 585
        distanceGreaterThan1000NotInt = 1856
        distanceGreaterThan1000Int = 2000

        self.assertEqual(views.formatDistance(distanceLessThan1000), "585m")
        self.assertEqual(views.formatDistance(
            distanceGreaterThan1000NotInt), "1.86Km")
        self.assertEqual(views.formatDistance(
            distanceGreaterThan1000Int), "2Km")

    def test_nearbyBusesFormatServiceName(self):
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

    def test_nearbyBusesFormatTime(self):
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
