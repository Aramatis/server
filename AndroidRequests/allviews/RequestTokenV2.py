from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

#python utilities
import hashlib
import os
from random import random
import uuid
import AndroidRequests.constants as Constants

# my stuff
# import DB's models
from AndroidRequests.models import Bus, Token, ActiveToken

class RequestTokenV2(View):
    """This class handles the start of the tracking, assigning a token
    to identify the trip, not the device."""

    def __init__(self):
        self.context={}

    def get(self, request, pUserId, pBusService, pUUID, data=timezone.now()):
        """ the token is primary a hash of the time stamp plus a random salt """
        salt = os.urandom(20)
        hashToken = hashlib.sha512( str(data) + salt ).hexdigest()

        # remove hyphen and convert to uppercase
        response = {}
        
        bus = Bus.objects.get(uuid = pUUID)[0]
        bus.service = pBusService
        bus.save()
        aToken = Token.objects.create(userId=pUserId, token=hashToken, bus=bus, \
                color=self.getRandomColor(), direction = None, uuid=pUUID)
            
        ActiveToken.objects.create(timeStamp=data,token=aToken)

        # we store the active token
        response['token'] = hashToken

        return JsonResponse(response, safe=False)

    def getRandomColor(self):
        # color used by web page that shows trip trajectories
        #unused -> letters = '0123456789ABCDEF0'
        color = '#'
        colors = {'#2c7fb8','#dd1c77','#016c59','#de2d26','#d95f0e'}
        color = list(colors)[int(round(random() * 4))]
        return color
