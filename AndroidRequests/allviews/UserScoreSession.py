from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import TranSappUser, Level
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

from google.oauth2 import id_token
from google.auth.transport import requests as googleRequests

import json
import logging
import uuid
import requests

NULL_SESSION_TOKEN = uuid.UUID('a81d843e65154f2894798fc436827b33')


class InvalidFacebookSessionException(Exception):
    pass


class InvalidGoogleSessionException(Exception):
    pass


class TranSappUserLogin(View):
    """ log in transapp user """

    def __init__(self):
        super(TranSappUserLogin, self).__init__()
        self.context = {}
        self.logger = logging.getLogger(__name__)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TranSappUserLogin, self).dispatch(request, *args, **kwargs)

    def checkGoogleId(self, accessToken):
        """ ask to google if accessToken is valid """
        try:
            idinfo = id_token.verify_oauth2_token(accessToken, googleRequests.Request(), settings.GOOGLE_LOGIN_KEY)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                #raise ValueError('Wrong issuer.')
                return None

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            userid = idinfo['sub']
            return userid

        except ValueError:
            return None

    def checkFacebookId(self, accessToken):
        """ ask to facebook if accessToken is valid """

        URL = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}|{}'. \
            format(accessToken, settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
        response = requests.get(URL, timeout=0.001)
        response = json.loads(response.text)

        if response['data'] and response['data']['is_valid'] and response['data']['app_id'] == settings.FACEBOOK_APP_ID:
            return response['data']['user_id']

        return None

    def post(self, request):
        """ register user """

        accessToken = request.POST.get('accessToken')
        accountType = request.POST.get('accountType')
        phoneId = request.POST.get('phoneId')
        name = request.POST.get('name')
        email = request.POST.get('email')
        userId = request.POST.get('userId')
        photoURI = request.POST.get('photoURI')
        nickname = request.POST.get('nickname')

        response = {}

        try:
            users = None

            if accountType == TranSappUser.FACEBOOK:
                facebookUserId = self.checkFacebookId(accessToken)

                if facebookUserId and userId == facebookUserId:
                    users = TranSappUser.objects.filter(userId=userId, accountType=TranSappUser.FACEBOOK)
                else:
                    raise InvalidFacebookSessionException
            elif accountType == TranSappUser.GOOGLE:
                googleUserId = self.checkGoogleId(accessToken)

                if googleUserId and userId == googleUserId:
                    users = TranSappUser.objects.filter(userId=userId, accountType=TranSappUser.GOOGLE)
                else:
                    raise InvalidGoogleSessionException

            sessionToken = uuid.uuid4()

            if users:
                # user exists
                user = users[0]
                user.phoneId = phoneId
                user.sessionToken = sessionToken
                user.photoURI = photoURI
                user.nickname = nickname
                user.timestamp = timezone.now()
                user.save()
            else:
                # user does not exist
                firstLevel = Level.objects.get(position=1)
                if TranSappUser.objects.count() > 0:
                    globalPosition, globalScore = TranSappUser.objects.order_by("-globalPosition").\
                        values_list("globalPosition", "globalScore")[0]
                    if globalScore != 0:
                        globalPosition += 1
                else:
                    globalPosition = 1
                user = TranSappUser.objects.create(userId=userId,
                                                   accountType=accountType,
                                                   name=name,
                                                   email=email,
                                                   phoneId=phoneId,
                                                   photoURI=photoURI,
                                                   nickname=nickname,
                                                   sessionToken=sessionToken,
                                                   globalPosition=globalPosition,
                                                   level=firstLevel)

            # ok
            Status.getJsonStatus(Status.OK, response)
            response['sessionToken'] = user.sessionToken
            response.update(user.getLoginData())
        except (InvalidFacebookSessionException, InvalidGoogleSessionException) as e:
            Status.getJsonStatus(Status.INVALID_USER, response)
            self.logger.error(str(e))
        except Exception as e:
            Status.getJsonStatus(Status.INTERNAL_ERROR, response)
            self.logger.error(str(e))

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)


class TranSappUserLogout(View):
    """ end session """

    def __init__(self):
        super(TranSappUserLogout, self).__init__()
        self.context = {}
        self.logger = logging.getLogger(__name__)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TranSappUserLogout, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ change session id to default value """

        userId = request.POST.get('userId')
        sessionToken = request.POST.get('sessionToken')

        response = {}
        try:
            user = TranSappUser.objects.get(userId=userId, sessionToken=sessionToken)
            user.sessionToken = NULL_SESSION_TOKEN
            user.save()

            Status.getJsonStatus(Status.OK, response)
        except (ObjectDoesNotExist, ValueError, ValidationError) as e:
            Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, response)
            self.logger.error(str(e))

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)


class UpdateTranSappUserSettings(View):
    """ update user info """

    def __init__(self):
        super(UpdateTranSappUserSettings, self).__init__()
        self.context = {}
        self.logger = logging.getLogger(__name__)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateTranSappUserSettings, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ register user """

        sessionToken = request.POST.get('sessionToken')
        userId = request.POST.get('userId')

        nickname = request.POST.get('nickname')
        userAvatarId = request.POST.get('userAvatarId')
        busAvatarId = request.POST.get('busAvatarId')
        showAvatar = request.POST.get('showAvatar')

        response = {}
        user = None
        try:
            user = TranSappUser.objects.get(userId=userId, sessionToken=sessionToken)
        except (ObjectDoesNotExist, ValueError, ValidationError) as e:
            Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, response)
            self.logger.error(str(e))

        try:
            if user:
                user.showAvatar = showAvatar in ['True', 'true', 1]
                user.nickname = nickname
                user.userAvatarId = int(userAvatarId)
                user.busAvatarId = int(busAvatarId)
                user.save()

                Status.getJsonStatus(Status.OK, response)
        except Exception as e:
            Status.getJsonStatus(Status.INTERNAL_ERROR, response)
            self.logger.error(str(e))

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
