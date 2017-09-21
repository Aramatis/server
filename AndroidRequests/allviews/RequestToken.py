# python utilities
import hashlib
import os
import uuid
from random import random

from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from AndroidRequests.models import Busv2, Busassignment, Token, ActiveToken
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.constants as Constants


class RequestToken(View):
    """This class handles the start of the tracking, assigning a token
    to identify the trip, not the device."""

    def __init__(self):
        super(RequestToken, self).__init__()
        self.context = {}

    def get(
            self,
            request,
            pPhoneId,
            pBusService,
            pRegistrationPlate,
            data=timezone.now()):
        """ the token is primary a hash of the time stamp plus a random salt """
        salt = os.urandom(20)
        hashToken = hashlib.sha512(str(data) + salt).hexdigest()

        # remove hyphen and convert to uppercase
        pRegistrationPlate = pRegistrationPlate.replace('-', '').upper()

        # bus = Bus.objects.get_or_create(registrationPlate = pRegistrationPlate, \
        #        service = pBusService)[0]
        # aToken = Token.objects.create(phoneId=pPhoneId, token=hashToken, bus=bus, \
        #        color=self.getRandomColor(), direction = None)
        if pRegistrationPlate == Constants.DUMMY_LICENSE_PLATE:
            puuid = uuid.uuid4()
            bus = Busv2.objects.create(
                registrationPlate=pRegistrationPlate, uuid=puuid)
            assignment = Busassignment.objects.create(
                uuid=bus, service=pBusService)
        else:
            bus = Busv2.objects.get_or_create(
                registrationPlate=pRegistrationPlate)[0]
            assignment = Busassignment.objects.get_or_create(
                uuid=bus, service=pBusService)[0]

        aToken = Token.objects.create(
            phoneId=pPhoneId,
            token=hashToken,
            busassignment=assignment,
            color=self.getRandomColor(),
            timeCreation=timezone.now(),
            direction=None)
        ActiveToken.objects.create(timeStamp=data, token=aToken)

        # we store the active token
        response = {'token': hashToken}

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def getRandomColor(self):
        # color used by web page that shows trip trajectories
        # unused -> letters = '0123456789ABCDEF0'
        colors = {'#2c7fb8', '#dd1c77', '#016c59', '#de2d26', '#d95f0e'}
        color = list(colors)[int(round(random() * 4))]
        return color
