# -*- coding: utf-8 -*-
from django.test import TestCase, RequestFactory
from django.conf import settings

from mock import Mock

from PredictorDTPM.webService.WebService import WebService


class ParserTest(TestCase):
    """ test method  """

    def setUp(self):
        """  """
        self.factory = RequestFactory()
        self.stopCode = 'PA433'
        url = 'dtpm/busStopInfo/{}/{}'.format(settings.SECRET_KEY, self.stopCode)
        self.request = self.factory.get(url)

    def get_mock_client(self, sud_answer):
        """  """
        # create mock of WebServiceClient instance
        client = Mock(spec=WebService.WebServiceClient)

        sudClient = Mock()
        sudClient.attach_mock(Mock(), "service")
        sudClient.service.configure_mock(**{"predictorParaderoServicio.return_value": sud_answer})

        client.client = sudClient
        client.prefix = "t"
        client.clientCode = "e"
        client.answerCode = "s"
        client.resCode = [{"code": "00"}]
        client.transactionId = 1

        return client

    def test_code00AndCode01(self):
        """ test situation when authority response routes with code 00 and 01  """
        sud_answer = {
            "fechaprediccion": "2017-09-22",
            "horaprediccion": "15:32",
            "nomett": "SEGUNDA TRANSVERSAL ESQ. / 3 NORTE",
            "paradero": "PI576",
            "respuestaParadero": None,
            "servicios": [
                [
                    {
                        "codigorespuesta": "00",
                        "distanciabus1": "2155",
                        "distanciabus2": "3095",
                        "horaprediccionbus1": "Entre 07 Y 11 min. ",
                        "horaprediccionbus2": "Entre 12 Y 18 min. ",
                        "ppubus1": "FLXJ-24",
                        "ppubus2": "FLXG-74",
                        "respuestaServicio": None,
                        "servicio": "I10",
                    },
                    {
                        "codigorespuesta": "01",
                        "distanciabus1": "1134",
                        "distanciabus2": None,
                        "horaprediccionbus1": "Menos de 5 min. ",
                        "horaprediccionbus2": None,
                        "ppubus1": "ZN-6513",
                        "ppubus2": None,
                        "respuestaServicio": None,
                        "servicio": "423",
                    }
                ]
            ],
            "urlLinkPublicidad": None,
            "urlPublicidad": "http://mkt.smsbus.cl/img/Cat11.jpg"
        }

        sud_client = self.get_mock_client(sud_answer)
        WebService.clientInstance = sud_client
        webService = WebService(self.request)

        webService.askForServices(self.stopCode)

    def test_code11(self):
        """ test situation when authority response routes with code 11 """
        sud_answer = {
            "fechaprediccion": "2017-09-22",
            "horaprediccion": "15:32",
            "nomett": "SEGUNDA TRANSVERSAL ESQ. / 3 NORTE",
            "paradero": "PI576",
            "respuestaParadero": None,
            "servicios": [
                [
                    {
                        "codigorespuesta": "11",
                        "distanciabus1": None,
                        "distanciabus2": None,
                        "horaprediccionbus1": None,
                        "horaprediccionbus2": None,
                        "ppubus1": None,
                        "ppubus2": None,
                        "respuestaServicio": "Fuera de horario de operacion para este paradero",
                        "servicio": "I10N",
                    },
                    {
                        "codigorespuesta": "10",
                        "distanciabus1": None,
                        "distanciabus2": None,
                        "horaprediccionbus1": None,
                        "horaprediccionbus2": None,
                        "ppubus1": None,
                        "ppubus2": None,
                        "respuestaServicio": "No hay buses que se dirijan al paradero.",
                        "servicio": "I13",
                    }
                ]
            ],
            "urlLinkPublicidad": None,
            "urlPublicidad": "http://mkt.smsbus.cl/img/Cat11.jpg"
        }

        sud_client = self.get_mock_client(sud_answer)
        WebService.clientInstance = sud_client
        webService = WebService(self.request)

        webService.askForServices(self.stopCode)

    def test_code23(self):
        """ test situation when authority response routes with code 11 """
        sud_answer = {
            "fechaprediccion": "2017-09-21",
            "horaprediccion": "23:56",
            "nomett": None,
            "paradero": "PH607",
            "respuestaParadero": "Paradero invalido.",
            "servicios": [
                [
                    {
                        "codigorespuesta": "23",
                        "distanciabus1": None,
                        "distanciabus2": None,
                        "horaprediccionbus1": None,
                        "horaprediccionbus2": None,
                        "ppubus1": None,
                        "ppubus2": None,
                        "respuestaServicio": "Paradero invalido.",
                        "servicio": None,
                    }
                ]
            ],
            "urlLinkPublicidad": None,
            "urlPublicidad": "http://mkt.smsbus.cl/img/Cat11.jpg"
        }

        sud_client = self.get_mock_client(sud_answer)
        WebService.clientInstance = sud_client
        webService = WebService(self.request)

        webService.askForServices(self.stopCode)