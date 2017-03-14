# encoding=utf-8
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import View

# python utilities
import logging
import requests
import uuid

from score.models import TranSappUser

# Create your views here.

class TranSappUserLogin(View):
    ''' log in transapp user '''

    def __init__(self):
        self.context = {}

    def checkGoogleId(self, googleId):
        ''' ask to facebook if tokenId is valid '''
        pass
    
    def checkFacebookId(self, facebookId):
        ''' ask to facebook if tokenId is valid '''

        URL = 'debug_token?input_token={}&access_token={}'.format(facebookId, )
        response = request.get()

        if response['data']:
            return response['data']['is_valid']

        return False

    def post(self, request):
        """ register user """

        tokenId = request.POST.get('userId')
        tokenType = request.POST.get('tokenType')
        phoneId = request.POST.get('phoneId')
        name = request.POST.get('name')
        email = request.POST.get('email')

        response = {}
        if tokenType == 'FACEBOOK' and self.checkFacebookId(tokenId):
            users = TranSappUser.objects.filter(tokenId=tokenId)
            sessionUUID = uuid.uuid4()
            if users:
                # user exists
                user = users[0]
                user.sessionId = sessionUUID
                user.save()
            else:
                # user does not exist
                TranSappUser.objects.create(tokenId=tokenId, 
                    socialNetwork=SOCIAL_NETWORK.FACEBOOK,
                    name=name,
                    email=email
                    sessionId=sessionUUID)

            response['status'] = 'ok'
            response['sessionId'] = user.sessionId

        elif: tokenType == 'GOOGLE' and self.checkGoogleId(tokenId):
            pass
            response['status'] = 'ok'
        else:
            response['status'] = 'error'
            response['message'] = 'Token id is not valid'

        return JsonResponse(response, safe=False)

class TranSappUserLogout(View):
    """ end session """

    def __init__(self):
        self.context = {}

    def post(self, request):
        ''' change session id to default value '''

        tokenId = request.POST.get('userId')
        sessionUUID = request.POST.get('sessionId')

        users = TranSappUser.objects.filter(tokenId=tokenId, sessionId=sessionUUID)

        response = {}
        if users:
            # user exists
            user = users[0]
            user = user.sessionId = None
            user.save()

            response['status'] = 'ok'
        else:
            response['status'] = 'error'
            response['message'] = 'pair does not match with any user'
        
        return JsonResponse(response, safe=False)
