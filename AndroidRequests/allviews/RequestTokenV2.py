# python utilities
import hashlib
import os
from random import random

from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# my stuff
# import DB's models
from AndroidRequests.models import Busv2, Busassignment, Token, ActiveToken, TranSappUser


class RequestTokenV2(View):
    """This class handles the start of the tracking, assigning a token
    to identify the trip, not the device."""

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RequestTokenV2, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ get in the bus """

        phoneId = request.POST.get('phoneId')
        route = request.POST.get('route')
        machineId = request.POST.get('machineId')
        userId = request.POST.get('userId')
        sessionToken = request.POST.get('sessionToken')
        
        return self.get(request, phoneId, route, machineId, userId, sessionToken)

    def get(self, request, pPhoneId, pBusService, pUUID, userId=None, sessionToken=None, data=timezone.now()):
        """  """

        salt = os.urandom(20)
        hashToken = hashlib.sha512(str(data) + salt).hexdigest()
        # the token is primary a hash of the time stamp plus a random salt 

        busv2 = Busv2.objects.get(uuid=pUUID)
        busassignment = Busassignment.objects.get_or_create(
            uuid=busv2, service=pBusService)[0]

        tranSappUser = None
        try:
            tranSappUser = TranSappUser.objects.get(userId=userId, sessionToken=sessionToken)
        except Exception:
            pass

        tokenObj = Token.objects.create(
            phoneId=pPhoneId,
            token=hashToken,
            busassignment=busassignment,
            color=self.getRandomColor(),
            tranSappUser=tranSappUser,
            timeCreation=data,
            direction=None)

        ActiveToken.objects.create(timeStamp=data, token=tokenObj)

        # we store the active token
        response = {'token': hashToken}

        return JsonResponse(response, safe=False)

    def getRandomColor(self):
        # color used by web page that shows trip trajectories
        # unused -> letters = '0123456789ABCDEF0'
        colors = {'#2c7fb8', '#dd1c77', '#016c59', '#de2d26', '#d95f0e'}
        color = list(colors)[int(round(random() * 4))]
        return color
