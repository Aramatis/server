# encoding=utf-8
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import View

# python utilities
import logging
import requests
import uuid
import re
import json

from score.models import TranSappUser, Level

NULL_SESSION_TOKEN = uuid.UUID('a81d843e65154f2894798fc436827b33')
# Create your views here.

class TranSappUserLogin(View):
    ''' log in transapp user '''

    def __init__(self):
        self.context = {}

    def checkGoogleId(self, googleId):
        ''' ask to facebook if tokenId is valid '''
        pass
    
    def checkFacebookId(self, accessToken):
        ''' ask to facebook if accessToken is valid '''

        APP_NAME = 'TranSapp'
        APP_ID = '371656789840491'
        APP_SECRET = 'b3027c1f591caa7ef9c2f7b2cc0c50af'
        URL = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}|{}'.format(accessToken, APP_ID, APP_SECRET)
        response = requests.get(URL)
        response = json.loads(response.text)
        
        if response['data'] and \
           response['data']['is_valid'] and \
           response['data']['app_id'] == APP_ID:
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
               
        response = {}
        response['status'] = 400
        response['message'] = 'Access token is not valid'
        if accountType == TranSappUser.FACEBOOK:
            facebookUserId = self.checkFacebookId(accessToken)
            if facebookUserId and userId == facebookUserId:
                # is a valid facebook user
                users = TranSappUser.objects.filter(userId=userId)
                sessionToken = uuid.uuid4()
                if users:
                    # user exists
                    user = users[0]
                    user.phoneId = phoneId
                    user.sessionToken = sessionToken
                    user.save()
                else:
                    # user does not exist
                    firstLevel = Level.objects.get(position=1)
                    user = TranSappUser.objects.create(userId=userId, 
                        accountType=TranSappUser.FACEBOOK,
                        name=name,
                        email=email,
                        phoneId=phoneId,
                        sessionToken=sessionToken, 
                        level=firstLevel)

                response['status'] = 200
                response['message'] = ':-)'
                response['sessionToken'] = user.sessionToken
                response['userData'] = {}
                response['userData']['score'] = user.globalScore
                response['userData']['level'] = {}
                response['userData']['level']['name'] = user.level.name
                response['userData']['level']['maxScore'] = 1000 #TODO: fixed this pls!!!

        elif accountType == TranSappUser.GOOGLE and self.checkGoogleId(tokenId):
            pass
        
        return JsonResponse(response, safe=False)

class TranSappUserLogout(View):
    """ end session """

    def __init__(self):
        self.context = {}

    def isValidUUID(self, value):
        ''' '''
        pattern = re.compile(r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')
        return pattern.match(value)

    def post(self, request):
        ''' change session id to default value '''

        userId = request.POST.get('userId')
        sessionToken = request.POST.get('sessionToken')
        
        
        if self.isValidUUID(sessionToken): 
            users = TranSappUser.objects.filter(userId=userId, sessionToken=sessionToken)
        else:
            users = []

        response = {}
        if users:
            # user exists
            user = users[0]
            user.sessionToken = NULL_SESSION_TOKEN
            user.save()

            response['status'] = 200
        else:
            response['status'] = 400
            response['message'] = 'pair does not match with any user'
        
        return JsonResponse(response, safe=False)


