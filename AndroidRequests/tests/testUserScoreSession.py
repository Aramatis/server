from django.conf import settings
from django.test import TestCase, Client

from AndroidRequests.allviews import UserScoreSession as uss
from AndroidRequests.models import TranSappUser, Level
from AndroidRequests.statusResponse import Status

import json
import uuid
import requests


class GoogleAPI:
    """ class to manipulate calls to google API """
    pass


class FacebookAPI:
    """ class to manipulate calls to facebook API """
    HOST = 'https://graph.facebook.com/v2.8/'
    APP_ACCESS_TOKEN_PARAM = 'access_token={}'.format(settings.FACEBOOK_APP_ACCESS_TOKEN)

    def __init__(self):
        pass

    def createTestuser(self):
        """ create a test user """

        ENDPOINT = settings.FACEBOOK_APP_ID + '/accounts/test-users?'
        url = self.HOST + ENDPOINT + self.APP_ACCESS_TOKEN_PARAM + '&installed={}&name={}'.format(True,
                                                                                                  'TranSapper testing')
        response = requests.post(url)
        json_response = json.loads(response.text)

        return json_response['id'], json_response['access_token']

    def deleteTestuser(self, userId):
        """ delete a test user """

        url = self.HOST + userId + '?' + self.APP_ACCESS_TOKEN_PARAM
        response = requests.delete(url)
        json_response = json.loads(response.text)

        return json_response


class UserLogTestCase(TestCase):
    """  """
    URL_PREFIX = '/android/'
    """
    def makeGetRequest(self, url, params = {}):
        
        URL = self.URL_PREFIX + url
        c = Client()
        response = c.get(URL, params)
        self.assertEqual(response.status_code, 200)

        return response
    """

    def makePostRequest(self, url, params=None):
        if params is None:
            params = {}
        url = self.URL_PREFIX + url
        c = Client()
        response = c.post(url, params)
        self.assertEqual(response.status_code, 200)

        return json.loads(response.content)

    def setUp(self):
        """   """
        # Insert levels
        Level.objects.create(name="firstLevel", minScore=0, maxScore=1000, position=1)
        Level.objects.create(name="secondLevel", minScore=1000, maxScore=2000, position=2)

        self.NAME = 'test name'
        self.EMAIL = 'felipe@hernandez.cl'
        self.PHONE_ID_1 = 'c1f8c203-7285-481b-9fbe-5d13d375e0d5'
        self.PHONE_ID_2 = '2fe70cbb-6beb-473f-8fc4-0ff2042f1608'
        self.PHOTO_URI = 'aaa.aaaa.com/asdasdasd/photo'
        self.NICKNAME = 'nickname'

        self.facebook = FacebookAPI()
        self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP = self.facebook.createTestuser()

        # access token of fake user
        self.FACEBOOK_ACCESS_TOKEN_WITH_NOT_LOGGED_APP = 'EAAFSBRbv0msBABlfTcAdq8i61IKGqeYMUPmF8aZBEbRIU11WNlTqcRekCWZASa8xo0piQL1ZBHlFF2vSGStnf45gAWkLh3bcbZCSJCE8P6FHyMZBNVw0sFt860BY4Y8wR7ZCtCOwmwCwb20GoUIsSR7cgd2Xnc2QXkd8mlu4ss3cK8GOQgH15IEtt1Ef6fdJx6thTL5ZAgWzfdipeFUcSGd4f0Cl62Y3I4ZD'
        self.FAKE_ACCESS_TOKEN = 'EAAFSBRbv0msBABlfTcAdq8i61IKGqeYMUPmF8aZBEbRIU11WNlTqcRekCWZASa8xo0piQL1ZBHlFF2vSGStnf45gAWkLh3bcbZCSJCE8P6FHyMZBNVw0sFt860BY4Y8wR7ZCtCOwmwCwb20GoUIsSR7cgd2Xnc2QXkd8mlu4ss3cK8GOQgH15IEtt1Ef6fdJx6thTL5ZAgWzfdipeFUcSGd4f0Cl62Y3I4Zx'

    def tearDown(self):
        """ executed after each test method """
        self.facebook.deleteTestuser(self.USER_ID)

    def login(self, user_id, access_token, phone_id, account_type):
        """ log in a user """
        url = 'login'
        params = {
            'accessToken': access_token,
            'accountType': account_type,
            'phoneId': phone_id,
            'name': self.NAME,
            'email': self.EMAIL,
            'userId': user_id,
            'photoURI': self.PHOTO_URI,
            'nickname': self.NICKNAME
        }
        json_response = self.makePostRequest(url, params)

        return json_response

    def logout(self, user_id, session_token):
        """ log out a user """
        url = 'logout'
        params = {
            'userId': user_id,
            'sessionToken': session_token,
        }
        json_response = self.makePostRequest(url, params)

        return json_response

    def testFacebookLoginTwoUsers(self):
        """ log in two users to test global position logic """

        self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1, TranSappUser.FACEBOOK)
        self.assertEquals(TranSappUser.objects.count(), 1)
        TranSappUser.objects.update(globalScore=100)
        self.assertEquals(TranSappUser.objects.order_by("id").first().globalPosition, 1)

        user_id2, facebook_access_token2 = self.facebook.createTestuser()
        self.login(user_id2, facebook_access_token2, self.PHONE_ID_2, TranSappUser.FACEBOOK)
        self.facebook.deleteTestuser(user_id2)

        self.assertEquals(TranSappUser.objects.count(), 2)

        user_id3, facebook_access_token3 = self.facebook.createTestuser()
        self.login(user_id3, facebook_access_token3, uuid.uuid4(), TranSappUser.FACEBOOK)
        self.facebook.deleteTestuser(user_id3)
        self.assertEquals(TranSappUser.objects.order_by("-id")[1].globalPosition, 2)

        self.assertEquals(TranSappUser.objects.count(), 3)
        self.assertEquals(TranSappUser.objects.order_by("-id").first().globalPosition, 2)

    def testFacebookLogInWithRealAccessToken(self):
        """   """
        # login
        json_response = self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1,
                                   TranSappUser.FACEBOOK)

        self.assertEqual(json_response['status'], 200)
        self.assertIn("id", json_response['userData'].keys())
        self.assertIn("globalPosition", json_response['userData']["ranking"].keys())
        self.assertEqual(json_response['userData']['score'], 0)
        self.assertEqual(json_response['userData']['level']['name'], 'firstLevel')
        self.assertEqual(json_response['userData']['level']['position'], 1)
        self.assertEqual(json_response['userData']['level']['maxScore'], 1000)
        self.assertEqual(json_response['userData']['level']['minScore'], 0)
        self.assertEqual(json_response['userSettings']['busAvatarId'], 1)
        self.assertEqual(json_response['userSettings']['userAvatarId'], 1)
        self.assertEqual(json_response['userSettings']['showAvatar'], True)
        uuid.UUID(json_response['sessionToken'])

        # verify database
        self.assertEqual(TranSappUser.objects.count(), 1)
        user = TranSappUser.objects.first()
        self.assertEqual(user.sessionToken, uuid.UUID(json_response['sessionToken']))
        self.assertEqual(user.name, self.NAME)
        self.assertEqual(user.email, self.EMAIL)
        self.assertEqual(user.phoneId, uuid.UUID(self.PHONE_ID_1))
        self.assertEqual(user.photoURI, self.PHOTO_URI)
        self.assertEqual(user.nickname, self.NICKNAME)

        # the same user will log in on another phone
        json_response = self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_2,
                                   TranSappUser.FACEBOOK)

        self.assertEqual(TranSappUser.objects.count(), 1)
        user = TranSappUser.objects.first()
        self.assertEqual(user.sessionToken, uuid.UUID(json_response['sessionToken']))
        self.assertEqual(user.name, self.NAME)
        self.assertEqual(user.email, self.EMAIL)
        self.assertEqual(user.phoneId, uuid.UUID(self.PHONE_ID_2))

    def testFacebbokLoginWithRealAccessTokenButBadPhoneId(self):
        """   """
        json_response = self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, 'asdasd',
                                   TranSappUser.FACEBOOK)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.INTERNAL_ERROR, {})['status'])
        self.assertEqual(json_response['message'], Status.getJsonStatus(Status.INTERNAL_ERROR, {})['message'])

    def testFacebookLoginWithFakeAccessToken(self):
        """   """
        json_response = self.login(self.USER_ID, self.FAKE_ACCESS_TOKEN, self.PHONE_ID_1, TranSappUser.FACEBOOK)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.INVALID_USER, {})['status'])
        self.assertEqual(json_response['message'], Status.getJsonStatus(Status.INVALID_USER, {})['message'])

    def testFacebookLogout(self):
        """   """
        # login
        json_login = self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1,
                                TranSappUser.FACEBOOK)
        # logout
        json_logout = self.logout(self.USER_ID, json_login['sessionToken'])

        # tests
        self.assertEqual(json_logout['status'], Status.getJsonStatus(Status.OK, {})['status'])
        user = TranSappUser.objects.get(userId=self.USER_ID)
        self.assertEqual(user.sessionToken, uss.NULL_SESSION_TOKEN)

    def testFacebookLogoutWithBadSessionToken(self):
        """   """

        # login
        self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1, TranSappUser.FACEBOOK)
        # logout
        json_logout = self.logout(self.USER_ID, "I'm a bad session token")
        # tests
        self.assertEqual(json_logout['status'], Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])
        self.assertEqual(json_logout['message'], Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['message'])

    def testFacebookModifyUserInfo(self):
        """ modify user info  """
        # login
        json_response = self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1,
                                   TranSappUser.FACEBOOK)

        url = 'updateUserSettings'

        session_token = json_response['sessionToken']
        user_id = self.USER_ID
        nickname = "new nickname"
        user_avatar_id = 2
        bus_avatar_id = 2
        show_avatar = False

        data = {"sessionToken": session_token, "userId": user_id, "nickname": nickname, "userAvatarId": user_avatar_id,
                "busAvatarId": bus_avatar_id, "showAvatar": show_avatar}

        json_response = self.makePostRequest(url, data)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        user = TranSappUser.objects.get(userId=self.USER_ID)
        self.assertEqual(user.nickname, nickname)
        self.assertEqual(user.userAvatarId, user_avatar_id)
        self.assertEqual(user.busAvatarId, bus_avatar_id)
        self.assertEqual(user.showAvatar, show_avatar)

        # change avatar id
        data['showAvatar'] = True
        json_response = self.makePostRequest(url, data)
        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.OK, {})['status'])
        user = TranSappUser.objects.get(userId=self.USER_ID)
        self.assertEqual(user.showAvatar, True)

    def testFacebookModifyUserInfoWithFakeUserId(self):
        """ modify user info  """

        url = 'updateUserSettings'

        session_token = "fakeSessionToken"
        user_id = "fakeUserId"
        nickname = "new nickname"
        user_avatar_id = 2
        bus_avatar_id = 2
        show_avatar = False

        data = {"sessionToken": session_token, "userId": user_id, "nickname": nickname, "userAvatarId": user_avatar_id,
                "busAvatarId": bus_avatar_id, "showAvatar": show_avatar}

        json_response = self.makePostRequest(url, data)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])

    def testFacebookModifyUserInfoWithIncorrectData(self):
        """ modify user info with bad format """
        # login
        json_response = self.login(self.USER_ID, self.FACEBOOK_ACCESS_TOKEN_WITH_LOGGED_APP, self.PHONE_ID_1,
                                   TranSappUser.FACEBOOK)

        url = 'updateUserSettings'

        nickname = "new nickname"
        user_avatar_id = 2
        bus_avatar_id = "thisIsAnError"
        show_avatar = False

        data = {"sessionToken": json_response["sessionToken"], "userId": self.USER_ID, "nickname": nickname,
                "userAvatarId": user_avatar_id, "busAvatarId": bus_avatar_id, "showAvatar": show_avatar}

        json_response = self.makePostRequest(url, data)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.INTERNAL_ERROR, {})['status'])
