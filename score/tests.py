from django.test import TestCase, Client
from django.conf import settings

import uuid
import json
import requests

# Create your tests here.
from score.views import TranSappUserLogin, TranSappUserLogout
from score import views
from score.models import TranSappUser, Level

class FacebookAPI():
    ''' class to manipulate calls to facebook API '''
    HOST = 'https://graph.facebook.com/v2.8/'
    APP_ACCESS_TOKEN_PARAM = 'access_token={}'.format(settings.FACEBOOK_APP_ACCESS_TOKEN)

    def __init__(self):
        pass

    def createTestuser(self):
        ''' create a test user '''

        ENDPOINT = settings.FACEBOOK_APP_ID + '/accounts/test-users?'
        URL = self.HOST + ENDPOINT + self.APP_ACCESS_TOKEN_PARAM  + '&installed={}&name={}'.format(True, 'TranSapper testing')
        response = requests.post(URL)
        jsonResponse = json.loads(response.text)
        
        return jsonResponse['id'], jsonResponse['access_token']

    def deleteTestuser(self, userId):
        ''' delete a test user '''

        URL = self.HOST + userId + '?' + self.APP_ACCESS_TOKEN_PARAM
        response = requests.delete(URL)
        jsonResponse = json.loads(response.text)
        
        return jsonResponse


class UserLogTestCase(TestCase):
    '''  '''
    URL_PREFIX = '/score/'
    """
    def makeGetRequest(self, url, params = {}):
        
        URL = self.URL_PREFIX + url
        c = Client()
        response = c.get(URL, params)
        self.assertEqual(response.status_code, 200)

        return response
    """
    def makePostRequest(self, url, params = {}):
        
        URL = self.URL_PREFIX + url
        c = Client()
        response = c.post(URL, params)
        self.assertEqual(response.status_code, 200)

        return response

    def setUp(self):
        '''   '''
        # Insert levels
        Level.objects.create(name="firstLevel", minScore=0, position=1)
        Level.objects.create(name="secondLevel", minScore=1000, position=2)

        self.NAME = 'test name'
        self.EMAIL = 'felipe@hernandez.cl'
        self.PHONE_ID_1 = 'c1f8c203-7285-481b-9fbe-5d13d375e0d5'
        self.PHONE_ID_2 = '2fe70cbb-6beb-473f-8fc4-0ff2042f1608'
 
        self.facebook = FacebookAPI()
        self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP = self.facebook.createTestuser()

        # access token of fake user
        self.FACEBOOK_ACCESS_TOKEN_WITH_NOT_LOGGED_APP = 'EAAFSBRbv0msBABlfTcAdq8i61IKGqeYMUPmF8aZBEbRIU11WNlTqcRekCWZASa8xo0piQL1ZBHlFF2vSGStnf45gAWkLh3bcbZCSJCE8P6FHyMZBNVw0sFt860BY4Y8wR7ZCtCOwmwCwb20GoUIsSR7cgd2Xnc2QXkd8mlu4ss3cK8GOQgH15IEtt1Ef6fdJx6thTL5ZAgWzfdipeFUcSGd4f0Cl62Y3I4ZD'
        self.FAKE_ACCESS_TOKEN = 'EAAFSBRbv0msBABlfTcAdq8i61IKGqeYMUPmF8aZBEbRIU11WNlTqcRekCWZASa8xo0piQL1ZBHlFF2vSGStnf45gAWkLh3bcbZCSJCE8P6FHyMZBNVw0sFt860BY4Y8wR7ZCtCOwmwCwb20GoUIsSR7cgd2Xnc2QXkd8mlu4ss3cK8GOQgH15IEtt1Ef6fdJx6thTL5ZAgWzfdipeFUcSGd4f0Cl62Y3I4Zx'

    def tearDown(self):
        ''' executed after each test method '''
        self.facebook.deleteTestuser(self.USER_ID)

    def login(self, accessToken, phoneId, accountType):
        ''' log in a user '''
        url = 'login'
        params = {
            'accessToken': accessToken,
            'accountType': accountType,
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

    def testFacebookLogInWithRealAccessToken(self):
        '''   '''
        # login
        jsonResponse = self.login(self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1, TranSappUser.FACEBOOK)
 
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
        jsonResponse = self.login(self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_2, TranSappUser.FACEBOOK)

        self.assertEqual(TranSappUser.objects.count(), 1)
        user = TranSappUser.objects.first()
        self.assertEqual(user.sessionToken, uuid.UUID(jsonResponse['sessionToken']))
        self.assertEqual(user.name, self.NAME)
        self.assertEqual(user.email, self.EMAIL)
        self.assertEqual(user.phoneId, uuid.UUID(self.PHONE_ID_2))
    
    def testFacebbokLoginWithRealAccessTokenButBadPhoneId(self):
        '''   '''
        jsonResponse = self.login(self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, 'asdasd', TranSappUser.FACEBOOK)
        self.assertEqual(jsonResponse['status'], 400)

    def testFacebookLoginWithFakeAccessToken(self):
        '''   '''
        jsonResponse = self.login(self.FAKE_ACCESS_TOKEN, self.PHONE_ID_1, TranSappUser.FACEBOOK)
        self.assertEqual(jsonResponse['status'], 400)
    
    def testFacebookLogout(self):
        '''   '''
        # login
        jsonLogin = self.login(self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1, TranSappUser.FACEBOOK)
        # logout
        jsonLogout = self.logout(jsonLogin['sessionToken'])

        # tests
        self.assertEqual(jsonLogout['status'], 200)
        user = TranSappUser.objects.get(userId=self.USER_ID)
        self.assertEqual(user.sessionToken, views.NULL_SESSION_TOKEN)
    
    def testFacebookLogoutWithBadSessionToken(self):
        '''   '''

        # login
        jsonLogin = self.login(self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1, TranSappUser.FACEBOOK)
        # logout
        jsonLogout = self.logout("I'm a bad session token")
        # tests
        self.assertEqual(jsonLogout['status'], 400)
    
