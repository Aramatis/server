# encoding=utf-8
import json
# python utilities
import logging
import uuid

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import TranSappUser, Level
from AndroidRequests.statusResponse import Status

NULL_SESSION_TOKEN = uuid.UUID('a81d843e65154f2894798fc436827b33')

# Create your views here.


class TranSappUserLogin(View):
    """ log in transapp user """

    def __init__(self):
        self.context = {}
        self.logger = logging.getLogger(__name__)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TranSappUserLogin, self).dispatch(request, *args, **kwargs)

    # def checkGoogleId(self, googleId):
    #    """ ask to facebook if tokenId is valid """
    #    pass

    def checkFacebookId(self, accessToken):
        """ ask to facebook if accessToken is valid """

        URL = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}|{}'. \
            format(accessToken, settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
        response = requests.get(URL)
        response = json.loads(response.text)

        if response['data'] and \
                response['data']['is_valid'] and \
                        response['data']['app_id'] == settings.FACEBOOK_APP_ID:
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
        # access token invalid
        Status.getJsonStatus(Status.INVALID_ACCESS_TOKEN, response)

        if accountType == TranSappUser.FACEBOOK:
            facebookUserId = self.checkFacebookId(accessToken)

            if facebookUserId and userId == facebookUserId:
                # is a valid facebook user
                users = TranSappUser.objects.filter(userId=userId)
                sessionToken = uuid.uuid4()

                try:
                    if users:
                        # user exists
                        user = users[0]
                        user.phoneId = phoneId
                        user.sessionToken = sessionToken
                        user.photoURI = photoURI
                        user.nickname = nickname
                        user.save()
                    else:
                        # user does not exist
                        firstLevel = Level.objects.get(position=1)
                        user = TranSappUser.objects.create(userId=userId,
                                                           accountType=TranSappUser.FACEBOOK,
                                                           name=name,
                                                           email=email,
                                                           phoneId=phoneId,
                                                           photoURI=photoURI,
                                                           nickname=nickname,
                                                           sessionToken=sessionToken,
                                                           level=firstLevel)

                    # ok
                    Status.getJsonStatus(Status.OK, response)
                    response['sessionToken'] = user.sessionToken
                    response['userData'] = {}
                    response['userData']['score'] = user.globalScore
                    response['userData']['level'] = {}
                    response['userData']['level']['name'] = user.level.name
                    response['userData']['level']['maxScore'] = user.level.maxScore
                    response['userData']['level']['position'] = user.level.position
                    response['userSettings'] = {}
                    response['userSettings']['busAvatarId'] = user.busAvatarId
                    response['userSettings']['userAvatarId'] = user.userAvatarId
                    response['userSettings']['showAvatar'] = user.showAvatar
                except Exception as e:
                    Status.getJsonStatus(Status.INTERNAL_ERROR, response)
                    self.logger.error(str(e))
        # elif accountType == TranSappUser.GOOGLE:
        #    googleUserId = self.checkGoogleId(tokenId)

        return JsonResponse(response, safe=False)


class TranSappUserLogout(View):
    """ end session """

    def __init__(self):
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

        return JsonResponse(response, safe=False)


class UpdateTranSappUserSettings(View):
    """ update user info """

    def __init__(self):
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

        return JsonResponse(response, safe=False)
