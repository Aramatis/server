from django.test import TestCase, Client

import uuid

# Create your tests here.
from score.views import TranSappUserLogIn, TranSappUserLogOut


class UserLogTestCase(TestCase):
    '''  '''
    URL_PREFIX = '/score/'

    def makeGetRequest(self, url, params = {}):
        
        URL = UserLogTestCase.URL_PREFIX + url
        c = Client()
        response = c.get(URL, params)
        self.assertEqual(response.status_code, 200)

        return response

    def makePostRequest(self, url, params = {}):
        
        URL = UserLogTestCase.URL_PREFIX + url
        c = Client()
        response = c.post(URL, params)
        self.assertEqual(response.status_code, 200)

        return response

    def setUp(self):
        '''   '''
        pass

    def testLogIn(self):
        '''   '''
        url = 'login'
        params = {
            userId: 'asd'
            tokenType: 'FACEBOOK'
            phoneId: uuid.uuid4()
            name:  'test name'
            email: 'a@b.com'
        }
        response = self.makePostRequest(url, params)
        jsonResponse = json.loads(response.content)

    def testLogOut(self):
        '''   '''
        url = 'logout'
        params = {
            userId: ''
            sessionId: ''
        }
        response = self.makePostRequest(url, params)
        jsonResponse = json.loads(response.content)


        """
        - login malo -> mensaje de error
        - login bueno -> mensaje de exito
        - logout malo -> mensaje de error
        - logout bueno -> mensaje de existo
        """
