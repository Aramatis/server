import json
import random
import uuid

from django.test import TestCase, Client

# Create your tests here.
from AndroidRequests.models import TranSappUser, Level
from AndroidRequests.statusResponse import Status
from AndroidRequests.allviews.UserRanking import UserRanking


class UserRankingTestCase(TestCase):
    """  """
    URL_PREFIX = '/android/'

    def makeGetRequest(self, url, params=None):

        if params is None:
            params = {}
        URL = self.URL_PREFIX + url
        c = Client()
        response = c.get(URL, params)
        self.assertEqual(response.status_code, 200)

        return json.loads(response.content)

    def createUsers(self, userQuantity, userPosition, userObj):
        """ create @quantity users and put the user asked in @userPosition """

        phoneId = uuid.UUID('56fbbcbf-e48a-458a-9645-65ab145e35ea')
        score = 1000000
        for index in range(userQuantity):
            if index == userPosition - 1:
                userObj.globalScore = score
                userObj.save()
            else:
                name = "name{}".format(index + 1)
                nickname = "nickname{}".format(index + 1)
                userId = "userId{}".format(index + 1)
                showAvatar = bool(random.getrandbits(1))
                photoURI = 'thisIsAPhotoURI'
                sessionToken = uuid.uuid4()
                TranSappUser.objects.create(userId=userId,
                                            sessionToken=sessionToken, name=name, nickname=nickname,
                                            phoneId=phoneId, accountType=TranSappUser.FACEBOOK,
                                            level=self.level, globalScore=score, showAvatar=showAvatar,
                                            photoURI=photoURI)

            score -= 100

    def checkRankingList(self, userId, sessionToken, userPosition, topUserNumber, nearUserNumber):
        """ check ranking list returned by url """
        URL = 'getRanking'
        data = {
            "userId": userId,
            "sessionToken": sessionToken
        }
        jsonResponse = self.makeGetRequest(URL, data)

        self.assertEqual(jsonResponse['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])

        topRanking = jsonResponse['ranking']['top']
        self.assertEqual(len(topRanking), topUserNumber)
        previousScore = None
        previousPosition = None
        for index, user in enumerate(topRanking):
            if index == userPosition - 1:
                self.assertEqual(user['nickname'], self.NICKNAME)
                self.assertEqual(user['showAvatar'], self.SHOW_AVATAR)
                if not user['showAvatar']:
                    self.assertEqual(user['photoURI'], self.PHOTO_URI)

            if user['showAvatar']:
                self.assertTrue(user['userAvatarId'])
            else:
                self.assertTrue(user['photoURI'])

            if previousScore is not None:
                self.assertTrue(previousScore > user['globalScore'])
            if previousPosition is not None:
                self.assertTrue(previousPosition < user['position'])

            previousScore = user['globalScore']
            previousPosition = user['position']

        nearRanking = jsonResponse['ranking']['near']
        self.assertEqual(len(nearRanking), nearUserNumber)
        previousScore = None
        previousPosition = None
        delta = nearRanking[0]['position']
        for index, user in enumerate(nearRanking):
            if index + delta == userPosition:
                self.assertEqual(user['nickname'], self.NICKNAME)
                self.assertEqual(user['showAvatar'], self.SHOW_AVATAR)
                if not user['showAvatar']:
                    self.assertEqual(user['photoURI'], self.PHOTO_URI)

            if user['showAvatar']:
                self.assertTrue(user['userAvatarId'])
            else:
                self.assertTrue(user['photoURI'])

            if previousScore is not None:
                self.assertTrue(previousScore > user['globalScore'])
            if previousPosition is not None:
                self.assertTrue(previousPosition < user['position'])

            previousScore = user['globalScore']
            previousPosition = user['position']

    def setUp(self):
        """   """
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
                                                sessionToken=self.SESSION_TOKEN, name=self.NAME,
                                                showAvatar=self.SHOW_AVATAR,
                                                phoneId=uuid.UUID(self.PHONE_ID), accountType=TranSappUser.FACEBOOK,
                                                level=self.level, userAvatarId=self.USER_AVATAR_ID,
                                                photoURI=self.PHOTO_URI)

    def testUserDoesNotExist(self):
        """ user without session ask for ranking """
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
        """ user without session ask for ranking """
        URL = 'getRanking'
        userId = self.USER_ID
        sessionToken = uuid.uuid4()

        data = {
            "userId": userId,
            "sessionToken": sessionToken
        }
        jsonResponse = self.makeGetRequest(URL, data)

        self.assertEqual(jsonResponse['status'], Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])

    def testDoNotSendParams(self):
        """ user without session ask for ranking """
        URL = 'getRanking'

        data = {}
        jsonResponse = self.makeGetRequest(URL, data)

        self.assertEqual(jsonResponse['status'],
                         Status.getJsonStatus(Status.INVALID_PARAMS, {})['status'])

    def testUserOnTopFive(self):
        """   """
        userQuantity = 5
        userPosition = 3
        self.createUsers(userQuantity, userPosition, self.user)

        topUserQuantity = UserRanking.TOP_USERS if userQuantity > UserRanking.TOP_USERS else userQuantity

        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, topUserQuantity, userQuantity)

    def testUserOnTopTen(self):
        """   """
        userQuantity = 10
        userPosition = 7
        self.createUsers(userQuantity, userPosition, self.user)

        userQuantityResult = UserRanking.UPPER_USERS + 1 + (userQuantity - userPosition if userQuantity - userPosition < UserRanking.LOWER_USERS else UserRanking.LOWER_USERS)
        topUserQuantity = UserRanking.TOP_USERS if userQuantity > UserRanking.TOP_USERS else userQuantity

        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, topUserQuantity, userQuantityResult)

    def testUserOnTopTwenty(self):
        """   """
        userQuantity = 20
        userPosition = 18
        self.createUsers(userQuantity, userPosition, self.user)

        userQuantityResult = UserRanking.UPPER_USERS + 1 + (userQuantity-userPosition if userQuantity-userPosition < UserRanking.LOWER_USERS else UserRanking.LOWER_USERS)
        topUserQuantity = UserRanking.TOP_USERS if userQuantity > UserRanking.TOP_USERS else userQuantity
        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, topUserQuantity, userQuantityResult)

    def testUserOnTopOne(self):
        """   """
        userQuantity = 100
        userPosition = 1
        self.createUsers(userQuantity, userPosition, self.user)

        userQuantityResult = 5
        topUserQuantity = UserRanking.TOP_USERS if userQuantity > UserRanking.TOP_USERS else userQuantity
        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, userPosition, topUserQuantity, userQuantityResult)
