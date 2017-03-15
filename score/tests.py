from django.test import TestCase, Client

import uuid
import json

# Create your tests here.
from score.views import TranSappUserLogin, TranSappUserLogout
from score import views
from score.models import TranSappUser, Level


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
        # Insert levels
        Level.objects.create(name="firstLevel", minScore=0, position=1)
        Level.objects.create(name="secondLevel", minScore=1000, position=2)

        self.NAME = 'test name'
        self.EMAIL = 'felipe@hernandez.cl'
        self.USER_ID = '10211203806510951'
        self.PHONE_ID_1 = 'c1f8c203-7285-481b-9fbe-5d13d375e0d5'
        self.PHONE_ID_2 = '2fe70cbb-6beb-473f-8fc4-0ff2042f1608'
        
        self.REAL_ACCESS_TOKEN = 'EAAFSBRbv0msBAEVseimzlcAVYEmdw3WRt8D4G0ZCQzNp02pznb7hQZC1mrlAamXfpFCqseDJ9L7NurGGfAQv1gDCEQkcic2RL1YI5e6lROMgdebAoUoT0ZAtXBbj2pxfP6hvZBehuYZB0YSzHcBUb1vBc2Y8Pigk9v0zURo0HAlqCidpZC4YxAGE2Ol81aeqdTZAusOcl3gTYn7Gx4Ul5qZC' 
        self.FAKE_ACCESS_TOKEN = 'EAAFSBRbv0msBAEVseimzlcAVYEmdw3WRt8D4G0ZCQzNp02pznb7hQZC1mrlAamXfpFCqseDJ9L7NurGGfAQv1gDCEQkcic2RL1YI5e6lROMgdebAoUoT0ZAtXBbj2pxfP6hvZBehuYZB0YSzHcBUb1vBc2Y8Pigk9v0zURo0HAlqCidpZC4YxAGE2Ol81aeqdTZAusOcl3gTYn7Gx4Ul5qZx'

    def login(self, accessToken, phoneId):
        ''' log in a user '''

        url = 'login'
        params = {
            'accessToken': accessToken,
            'accountType': TranSappUser.FACEBOOK,
            'phoneId': phoneId, 
            'name':  self.NAME,
            'email': self.EMAIL,
            'userId': self.USER_ID
        }
        response = self.makePostRequest(url, params)
        
        return json.loads(response.content)
 
    def logout(self, sessionToken):
        ''' log out a user '''
        url = 'logout'
        params = {
            'userId': self.USER_ID,
            'sessionToken': sessionToken,
        }
        response = self.makePostRequest(url, params)

        return json.loads(response.content)

    def testLogInWithRealAccessToken(self):
        '''   '''

        # login
        jsonResponse = self.login(self.REAL_ACCESS_TOKEN, self.PHONE_ID_1)
 
        self.assertEqual(jsonResponse['status'], 200)
        self.assertEqual(jsonResponse['userData']['score'], 0)
        self.assertEqual(jsonResponse['userData']['level']['name'], 'firstLevel')
        self.assertEqual(jsonResponse['userData']['level']['maxScore'], 1000)
        self.assertTrue(views.isValidUUID(jsonResponse['sessionToken']))

        # verify database
        self.assertEqual(TranSappUser.objects.count(), 1)
        user = TranSappUser.objects.first()
        self.assertEqual(user.sessionToken, uuid.UUID(jsonResponse['sessionToken']))
        self.assertEqual(user.name, self.NAME)
        self.assertEqual(user.email, self.EMAIL)
        self.assertEqual(user.phoneId, uuid.UUID(self.PHONE_ID_1))


        # the same user will log in on another phone
        jsonResponse = self.login(self.REAL_ACCESS_TOKEN, self.PHONE_ID_2)

        self.assertEqual(TranSappUser.objects.count(), 1)
        user = TranSappUser.objects.first()
        self.assertEqual(user.sessionToken, uuid.UUID(jsonResponse['sessionToken']))
        self.assertEqual(user.name, self.NAME)
        self.assertEqual(user.email, self.EMAIL)
        self.assertEqual(user.phoneId, uuid.UUID(self.PHONE_ID_2))


    def testLogInWithFakeAccessToken(self):
        '''   '''
        jsonResponse = self.login(self.FAKE_ACCESS_TOKEN, self.PHONE_ID_1)
        self.assertEqual(jsonResponse['status'], 400)

    def testLogInWithFakeAccessToken(self):
        '''   '''
        jsonResponse = self.login(self.REAL_ACCESS_TOKEN, 'asdasd')
        self.assertEqual(jsonResponse['status'], 400)


    def testLogOut(self):
        '''   '''

        # login
        jsonLogin = self.login(self.REAL_ACCESS_TOKEN, self.PHONE_ID_1)

        # logout
        jsonLogout = self.logout(jsonLogin['sessionToken'])

        # tests
        self.assertEqual(jsonLogout['status'], 200)
        user = TranSappUser.objects.get(userId=self.USER_ID)
        self.assertEqual(user.sessionToken, views.NULL_SESSION_TOKEN)


        """
        - login malo -> mensaje de error
        - login bueno -> mensaje de exito
        - logout malo -> mensaje de error
        - logout bueno -> mensaje de existo
        """
