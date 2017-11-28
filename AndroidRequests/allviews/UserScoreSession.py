from django.conf import settings
from django.core.exceptions import ValidationError
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
        self.logger = logging.getLogger(__name__)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TranSappUserLogin, self).dispatch(request, *args, **kwargs)

    def check_google_id(self, access_token):
        """ ask to google if access_token is valid """
        try:
            id_info = id_token.verify_oauth2_token(access_token, googleRequests.Request(), settings.GOOGLE_LOGIN_KEY)

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                # raise ValueError('Wrong issuer.')
                return None

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            user_id = id_info['sub']
            return user_id

        except ValueError:
            return None

    def check_facebook_id(self, access_token):
        """ ask to facebook if accessToken is valid """

        url = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}|{}'. \
            format(access_token, settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
        response = requests.get(url)
        response = json.loads(response.text)

        if response['data'] and response['data']['is_valid'] and response['data']['app_id'] == settings.FACEBOOK_APP_ID:
            return response['data']['user_id']

        return None

    def post(self, request):
        """ register user """

        access_token = request.POST.get('accessToken')
        account_type = request.POST.get('accountType')
        phone_id = request.POST.get('phoneId')
        name = request.POST.get('name')
        email = request.POST.get('email')
        user_id = request.POST.get('userId')
        photo_uri = request.POST.get('photoURI')
        nickname = request.POST.get('nickname')

        response = {}

        try:
            users = None

            if account_type == TranSappUser.FACEBOOK:
                facebook_user_id = self.check_facebook_id(access_token)

                if facebook_user_id and user_id == facebook_user_id:
                    users = TranSappUser.objects.filter(userId=user_id, accountType=TranSappUser.FACEBOOK)
                else:
                    raise InvalidFacebookSessionException
            elif account_type == TranSappUser.GOOGLE:
                google_user_id = self.check_google_id(access_token)

                if google_user_id and user_id == google_user_id:
                    users = TranSappUser.objects.filter(userId=user_id, accountType=TranSappUser.GOOGLE)
                else:
                    raise InvalidGoogleSessionException

            session_token = uuid.uuid4()

            if users:
                # user exists
                user = users[0]
                user.phoneId = phone_id
                user.sessionToken = session_token
                user.photoURI = photo_uri
                user.nickname = nickname
                user.timestamp = timezone.now()
                user.save()
            else:
                # user does not exist
                first_level = Level.objects.get(position=1)
                if TranSappUser.objects.count() > 0:
                    global_position, global_score = TranSappUser.objects.order_by("-globalPosition").\
                        values_list("globalPosition", "globalScore")[0]
                    if global_score != 0:
                        global_position += 1
                else:
                    global_position = 1
                user = TranSappUser.objects.create(userId=user_id,
                                                   accountType=account_type,
                                                   name=name,
                                                   email=email,
                                                   phoneId=phone_id,
                                                   photoURI=photo_uri,
                                                   nickname=nickname,
                                                   sessionToken=session_token,
                                                   globalPosition=global_position,
                                                   level=first_level)

            # ok
            Status.getJsonStatus(Status.OK, response)
            response['sessionToken'] = user.sessionToken
            response.update(user.get_login_data())
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

        user_id = request.POST.get('userId')
        session_token = request.POST.get('sessionToken')

        response = {}
        try:
            user = TranSappUser.objects.get(userId=user_id, sessionToken=session_token)
            user.sessionToken = NULL_SESSION_TOKEN
            user.save()

            Status.getJsonStatus(Status.OK, response)
        except (TranSappUser.DoesNotExist, ValueError, ValidationError) as e:
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

        session_token = request.POST.get('sessionToken')
        user_id = request.POST.get('userId')

        nickname = request.POST.get('nickname')
        user_avatar_id = request.POST.get('userAvatarId')
        bus_avatar_id = request.POST.get('busAvatarId')
        show_avatar = request.POST.get('showAvatar')

        response = {}
        user = None
        try:
            user = TranSappUser.objects.get(userId=user_id, sessionToken=session_token)
        except (TranSappUser.DoesNotExist, ValueError, ValidationError) as e:
            Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, response)
            self.logger.error(str(e))

        try:
            if user:
                user.showAvatar = show_avatar in ['True', 'true', 1]
                user.nickname = nickname
                user.userAvatarId = int(user_avatar_id)
                user.busAvatarId = int(bus_avatar_id)
                user.save()

                Status.getJsonStatus(Status.OK, response)
        except Exception as e:
            Status.getJsonStatus(Status.INTERNAL_ERROR, response)
            self.logger.error(str(e))

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
