from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from random import random

from AndroidRequests.models import Busv2, Busassignment, Token, ActiveToken
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.constants as constants
import hashlib
import os
import uuid


class RequestToken(View):
    """This class handles the start of the tracking, assigning a token
    to identify the trip, not the device."""

    def get(
            self,
            request,
            phone_od,
            route,
            license_plate,
            data=None):
        """ the token is primary a hash of the time stamp plus a random salt """
        if data is None:
            data = timezone.now()

        salt = os.urandom(20)
        hash_token = hashlib.sha512(str(data) + salt).hexdigest()

        # remove hyphen and convert to uppercase
        license_plate = license_plate.replace('-', '').upper()

        # bus = Bus.objects.get_or_create(registrationPlate = license_plate, \
        #        service = route)[0]
        # aToken = Token.objects.create(phoneId=phone_od, token=hashToken, bus=bus, \
        #        color=self.getRandomColor(), direction = None)
        if license_plate == constants.DUMMY_LICENSE_PLATE:
            machine_id = uuid.uuid4()
            bus = Busv2.objects.create(registrationPlate=license_plate, uuid=machine_id)
            bus_assignment = Busassignment.objects.create(uuid=bus, service=route)
        else:
            bus = Busv2.objects.get_or_create(
                registrationPlate=license_plate)[0]
            bus_assignment = Busassignment.objects.get_or_create(
                uuid=bus, service=route)[0]

        token_obj = Token.objects.create(
            phoneId=phone_od,
            token=hash_token,
            busassignment=bus_assignment,
            color=self.get_random_color(),
            timeCreation=data,
            direction=None)
        ActiveToken.objects.create(timeStamp=data, token=token_obj)

        # we store the active token
        response = {'token': hash_token}

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def get_random_color(self):
        # color used by web page that shows trip trajectories
        # unused -> letters = '0123456789ABCDEF0'
        colors = {'#2c7fb8', '#dd1c77', '#016c59', '#de2d26', '#d95f0e'}
        color = list(colors)[int(round(random() * 4))]
        return color
