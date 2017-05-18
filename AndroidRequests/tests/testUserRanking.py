from django.test import TestCase, Client
from django.conf import settings

import uuid
import json

# Create your tests here.
from AndroidRequests.allviews import UserScoreSession as uss
from AndroidRequests.models import TranSappUser, Level

from AndroidRequests.statusResponse import Status

class UserRankingTestCase(TestCase):
    '''  '''
    URL_PREFIX = '/android/'
    
    def makeGetRequest(self, url, params = {}):
        
        URL = self.URL_PREFIX + url
        c = Client()
        response = c.get(URL, params)
        self.assertEqual(response.status_code, 200)

        return json.loads(response.content)
    
    def createUsers(self, userQuantity, userPosition, userObj):
        ''' create @quantity users and put the user asked in @userPosition '''

        phoneId = uuid.UUID('56fbbcbf-e48a-458a-9645-65ab145e35ea')
        score = 1000000
        for index in range(userQuantity):
            if index == userPosition-1:
                userObj.globalScore = score
                userObj.save()
            else:
                name = "name{}".format(index+1)
                nickname = "nickname{}".format(index+1)
                userId = "userId{}".format(index+1)
                sessionToken = uuid.uuid4()
                TranSappUser.objects.create(userId=userId, 
                        sessionToken=sessionToken, name=name, nickname=nickname,
                        phoneId=phoneId, accountType=TranSappUser.FACEBOOK, 
                        level=self.level, globalScore=score)

            score -= 100

    def checkRankingList(self, userId, sessionToken, userPosition, resultUsersNumber):
        ''' check ranking list returned by url '''
        URL = 'getRanking'
        data = {
          "userId": userId,
          "sessionToken": sessionToken
        }
        jsonResponse = self.makeGetRequest(URL, data)

        self.assertEqual(jsonResponse['status'], 
                Status.getJsonStatus(Status.OK, {})['status'])

        ranking = jsonResponse['ranking']
        self.assertEqual(len(ranking), resultUsersNumber)
        previousScore = None
        previousPosition = None
        
        for index, user in enumerate(ranking):
            if index == userPosition-1:
                self.assertEqual(user['nickname'], self.NICKNAME)
                self.assertEqual(user['showAvatar'], self.SHOW_AVATAR)
                self.assertEqual(user['photoURI'], self.PHOTO_URI)
            
            if previousScore is not None:
                self.assertTrue(previousScore>user['globalScore'])
            if previousPosition is not None:
                self.assertTrue(previousPosition<user['position'])

            previousScore = user['globalScore']
            previousPosition = user['position']

    def setUp(self):
        '''   '''
        self.level = Level.objects.create(name="firstLevel", minScore=0, maxScore=2000000, position=1)

        self.NAME = 'test name'
        self.EMAIL = 'felipe@hernandez.cl'
        self.PHONE_ID = 'c1f8c203-7285-481b-9fbe-5d13d375e0d5'
        self.PHOTO_URI = 'aaa.aaaa.com/asdasdasd/photo'
        self.NICKNAME = 'nickname'
        self.USER_ID = '123456'
        self.SESSION_TOKEN = 'e496c175-c3a8-4ee1-83bb-5d6e6a2ed24b'
        self.USER_AVATAR_ID = 300
        self.SHOW_AVATAR = True

        self.user = TranSappUser.objects.create(userId=self.USER_ID, nickname=self.NICKNAME, 
                sessionToken=self.SESSION_TOKEN, name=self.NAME, showAvatar=self.SHOW_AVATAR, 
                phoneId=uuid.UUID(self.PHONE_ID), accountType=TranSappUser.FACEBOOK, 
                level=self.level, userAvatarId=self.USER_AVATAR_ID, photoURI=self.PHOTO_URI)

    def testUserDoesNotExist(self):
        ''' user without session ask for ranking '''
        URL = 'getRanking'
        userId = 'fakeUserId'
        sessionToken = uuid.uuid4()

        data = {
          "userId": userId,
          "sessionToken": sessionToken
        }
        jsonResponse = self.makeGetRequest(URL, data)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.INVALID_USER, {})['status'])

    def testInvalidSession(self):
        ''' user without session ask for ranking '''
        URL = 'getRanking'
        userId = self.USER_ID
        sessionToken = uuid.uuid4()

        data = {
          "userId": userId,
          "sessionToken": sessionToken
        }
        jsonResponse = self.makeGetRequest(URL, data)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])


    def testDontSendParams(self):
        ''' user without session ask for ranking '''
        URL = 'getRanking'

        data = {}
        jsonResponse = self.makeGetRequest(URL, {})

        self.assertEqual(jsonResponse['status'], 
                Status.getJsonStatus(Status.INVALID_PARAMS, {})['status'])


    def testUserOnTopFive(self):
        '''   '''
        userQuantity = 5
        userPosition = 3
        self.createUsers(userQuantity, userPosition, self.user)

        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, userQuantity)

    def testUserOnTopTen(self):
        '''   '''
        userQuantity = 10
        userPosition = 7
        self.createUsers(userQuantity, userPosition, self.user)

        userQuantityResult = 10
        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, userQuantityResult)

    def testUserOnTopTwenty(self):
        '''   '''
        userQuantity = 20
        userPosition = 18
        self.createUsers(userQuantity, userPosition, self.user)

        userQuantityResult = 13
        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, userQuantityResult)

    def testUserOnTopOne(self):
        '''   '''
        userQuantity = 100
        userPosition = 1
        self.createUsers(userQuantity, userPosition, self.user)

        userQuantityResult = 5
        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, userQuantityResult)





