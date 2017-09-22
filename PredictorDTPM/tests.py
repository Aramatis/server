# -*- coding: utf-8 -*-
from django.test import TestCase, RequestFactory
from django.conf import settings

from mock import MagicMock

from PredictorDTPM.webService.WebService import WebService


class ParserTest(TestCase):
    """ test method  """

    def setUp(self):
        """  """
        self.factory = RequestFactory()
        stopCode = 'PA433'
        url = 'dtpm/busStopInfo/{}/{}'.format(settings.SECRET_KEY, stopCode)
        request = self.factory.get(url)

        # it is necessary to don´t initialize instance
        WebService.clientInstance = []
        self.webService = WebService(request)
        data = self.webService.askForServices(stopCode)

        self.auth_answer = {

        }

    def test_er(self):
        """  """

        pass