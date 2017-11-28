from django.test import TestCase, Client
from django.utils import timezone

from AndroidRequests.models import TranSappUser, Level, ScoreHistory, ScoreEvent
from AndroidRequests.statusResponse import Status
from AndroidRequests.allviews.UserRanking import UserRanking

import json
import random
import uuid


class UserRankingTestCase(TestCase):
    """  """
    URL_PREFIX = '/android/'

    def makeGetRequest(self, url, params=None):

        if params is None:
            params = {}
        url = self.URL_PREFIX + url
        c = Client()
        response = c.get(url, params)
        self.assertEqual(response.status_code, 200)

        return json.loads(response.content)

    def createUsers(self, user_quantity, user_position, user_obj):
        """ create @quantity users and put the user asked in @user_position """

        phone_id = uuid.UUID('56fbbcbf-e48a-458a-9645-65ab145e35ea')
        score = 1000000

        position = 1
        for index in range(user_quantity):
            if index == user_position - 1:
                user_obj.globalScore = score
                user_obj.globalPosition = position
                user_obj.save()
            else:
                name = "name{}".format(index + 1)
                nickname = "nickname{}".format(index + 1)
                user_id = "userId{}".format(index + 1)
                show_avatar = bool(random.getrandbits(1))
                photo_uri = 'thisIsAPhotoURI'
                session_token = uuid.uuid4()
                TranSappUser.objects.create(userId=user_id,
                                            sessionToken=session_token, name=name, nickname=nickname,
                                            phoneId=phone_id, accountType=TranSappUser.FACEBOOK,
                                            level=self.level, globalScore=score, showAvatar=show_avatar,
                                            photoURI=photo_uri, globalPosition=position)
            score -= 100
            position += 1

    def checkRankingList(self, user_id, session_token, user_position, top_user_number, near_user_number):
        """ check ranking list returned by url """
        url = 'getRanking'
        data = {
            "userId": user_id,
            "sessionToken": session_token
        }
        json_response = self.makeGetRequest(url, data)

        self.assertEqual(json_response['status'],
                         Status.getJsonStatus(Status.OK, {})['status'])

        top_ranking = json_response['ranking']['top']
        self.assertEqual(len(top_ranking), top_user_number)
        previous_score = None
        previous_position = None
        for index, user in enumerate(top_ranking):
            if index == user_position - 1:
                self.assertEqual(user['nickname'], self.NICKNAME)
                self.assertEqual(user['showAvatar'], self.SHOW_AVATAR)
                if not user['showAvatar']:
                    self.assertEqual(user['photoURI'], self.PHOTO_URI)

            if user['showAvatar']:
                self.assertTrue(user['userAvatarId'])
            else:
                self.assertTrue(user['photoURI'])

            if previous_score is not None:
                self.assertTrue(previous_score > user['globalScore'])
            if previous_position is not None:
                self.assertTrue(previous_position < user["ranking"]['globalPosition'])

            previous_score = user['globalScore']
            previous_position = user["ranking"]['globalPosition']

        near_ranking = json_response['ranking']['near']
        self.assertEqual(len(near_ranking), near_user_number)
        previous_score = None
        previous_position = None
        delta = near_ranking[0]["ranking"]['globalPosition']
        for index, user in enumerate(near_ranking):
            if index + delta == user_position:
                self.assertEqual(user['nickname'], self.NICKNAME)
                self.assertEqual(user['showAvatar'], self.SHOW_AVATAR)
                if not user['showAvatar']:
                    self.assertEqual(user['photoURI'], self.PHOTO_URI)

            if user['showAvatar']:
                self.assertTrue(user['userAvatarId'])
            else:
                self.assertTrue(user['photoURI'])

            if previous_score is not None:
                self.assertTrue(previous_score > user['globalScore'])
            if previous_position is not None:
                self.assertTrue(previous_position < user["ranking"]['globalPosition'])

            previous_score = user['globalScore']
            previous_position = user["ranking"]['globalPosition']

    def setUp(self):
        """   """
        self.level = Level.objects.create(name="firstLevel", minScore=0, maxScore=2000000, position=1)

        self.NAME = 'test name'
        self.EMAIL = 'felipe@hernandez.cl'
        self.PHONE_ID = 'c1f8c203-7285-481b-9fbe-5d13d375e0d5'
        self.PHOTO_URI = 'aaa.aaaa.com/asdasdasd/photo'
        self.NICKNAME = 'testNickname'
        self.USER_ID = '123456'
        self.SESSION_TOKEN = 'e496c175-c3a8-4ee1-83bb-5d6e6a2ed24b'
        self.USER_AVATAR_ID = 300
        self.SHOW_AVATAR = True

        self.user = TranSappUser.objects.create(userId=self.USER_ID, nickname=self.NICKNAME,
                                                sessionToken=self.SESSION_TOKEN, name=self.NAME,
                                                showAvatar=self.SHOW_AVATAR,
                                                phoneId=uuid.UUID(self.PHONE_ID), accountType=TranSappUser.FACEBOOK,
                                                level=self.level, userAvatarId=self.USER_AVATAR_ID,
                                                photoURI=self.PHOTO_URI, globalPosition=1)
        # simulate a report to execute update
        score = ScoreEvent.objects.create(code="111", score=100)
        ScoreHistory.objects.create(tranSappUser_id=self.user.id, scoreEvent=score, timeCreation=timezone.now())

    def testUserDoesNotExist(self):
        """ user without session ask for ranking """
        url = 'getRanking'
        user_id = 'fakeUserId'
        session_token = uuid.uuid4()

        data = {
            "userId": user_id,
            "sessionToken": session_token
        }
        json_response = self.makeGetRequest(url, data)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.INVALID_USER, {})['status'])

    def testInvalidSession(self):
        """ user without session ask for ranking """
        url = 'getRanking'
        user_id = self.USER_ID
        session_token = uuid.uuid4()

        data = {
            "userId": user_id,
            "sessionToken": session_token
        }
        json_response = self.makeGetRequest(url, data)

        self.assertEqual(json_response['status'], Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, {})['status'])

    def testDoNotSendParams(self):
        """ user without session ask for ranking """
        url = 'getRanking'

        data = {}
        json_response = self.makeGetRequest(url, data)

        self.assertEqual(json_response['status'],
                         Status.getJsonStatus(Status.INVALID_PARAMS, {})['status'])

    def testUserOnTopFive(self):
        """   """
        user_quantity = 5
        user_position = 3
        self.createUsers(user_quantity, user_position, self.user)

        top_user_quantity = UserRanking.TOP_USERS if user_quantity > UserRanking.TOP_USERS else user_quantity

        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, user_position, top_user_quantity, user_quantity)

    def testUserOnTopTen(self):
        """   """
        user_quantity = 10
        user_position = 7
        self.createUsers(user_quantity, user_position, self.user)

        user_quantity_result = UserRanking.UPPER_USERS + 1 + (
        user_quantity - user_position if user_quantity - user_position < UserRanking.LOWER_USERS else UserRanking.LOWER_USERS)
        top_user_quantity = UserRanking.TOP_USERS if user_quantity > UserRanking.TOP_USERS else user_quantity

        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, user_position, top_user_quantity, user_quantity_result)

    def testUserOnTopTwenty(self):
        """   """
        user_quantity = 20
        user_position = 18
        self.createUsers(user_quantity, user_position, self.user)

        user_quantity_result = UserRanking.UPPER_USERS + 1 + (
        user_quantity - user_position if user_quantity - user_position < UserRanking.LOWER_USERS else UserRanking.LOWER_USERS)
        top_user_quantity = UserRanking.TOP_USERS if user_quantity > UserRanking.TOP_USERS else user_quantity
        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, user_position, top_user_quantity, user_quantity_result)

    def testUserOnTopOne(self):
        """   """
        user_quantity = 100
        user_position = 1
        self.createUsers(user_quantity, user_position, self.user)

        user_quantity_result = 5
        top_user_quantity = UserRanking.TOP_USERS if user_quantity > UserRanking.TOP_USERS else user_quantity
        self.checkRankingList(self.USER_ID, self.SESSION_TOKEN, user_position, top_user_quantity, user_quantity_result)
