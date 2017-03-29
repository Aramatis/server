# encoding=utf-8
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# python utilities
import logging
import requests
import uuid
import re
import json

from AndroidRequests.models import TranSappUser, Level

NULL_SESSION_TOKEN = uuid.UUID('a81d843e65154f2894798fc436827b33')
# Create your views here.

def isValidUUID(value):
    ''' '''
    pattern = re.compile(r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')
    return pattern.match(value)


class TranSappUserLogin(View):
    ''' log in transapp user '''

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TranSappUserLogin, self).dispatch(request, *args, **kwargs)

    def checkGoogleId(self, googleId):
        ''' ask to facebook if tokenId is valid '''
        pass
    
    def checkFacebookId(self, accessToken):
        ''' ask to facebook if accessToken is valid '''

        URL = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}|{}'.\
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
               
        response = {}
        response['status'] = 400
        response['message'] = 'Access token is not valid'

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
                    response['userData']['level']['maxScore'] = Level.objects.get(position=user.level.position+1).minScore
                except Exception as e:
                    print str(e)
        elif accountType == TranSappUser.GOOGLE:
            googleUserId = self.checkGoogleId(tokenId)
        
        return JsonResponse(response, safe=False)

class TranSappUserLogout(View):
    """ end session """

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TranSappUserLogout, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        ''' change session id to default value '''

        userId = request.POST.get('userId')
        sessionToken = request.POST.get('sessionToken')
        
        
        if isValidUUID(sessionToken): 
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


