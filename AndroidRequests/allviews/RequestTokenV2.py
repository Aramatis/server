from random import random

from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError

from AndroidRequests.models import Busv2, Busassignment, Token, ActiveToken, TranSappUser, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

import hashlib
import os
import logging


class RequestTokenV2(View):
    """This class handles the start of the tracking, assigning a token
    to identify the trip, not the device."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RequestTokenV2, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ get in the bus """

        phone_id = request.POST.get('phoneId')
        route = request.POST.get('route')
        machine_id = request.POST.get('machineId')
        user_id = request.POST.get('userId')
        session_token = request.POST.get('sessionToken')
        # current bus position
        bus_latitude = request.POST.get('latitude')
        bus_longitude = request.POST.get('longitude')

        return self.get(request, phone_id, route, machine_id, bus_latitude, bus_longitude, user_id, session_token)

    def get(self, request, phone_id, route, machine_id, bus_latitude=None, bus_longitude=None,
            user_id=None, session_token=None, timestamp=None):
        """  """

        if timestamp is None:
            timestamp = timezone.now()
        salt = os.urandom(20)
        hash_token = hashlib.sha512(str(timestamp) + salt).hexdigest()
        # the token is primary a hash of the time stamp plus a random salt

        response = {}
        try:
            with transaction.atomic():
                bus_obj = Busv2.objects.get(uuid=machine_id)
                bus_assignment = Busassignment.objects.get_or_create(uuid=bus_obj, service=route)[0]

                transapp_user = None
                try:
                    transapp_user = TranSappUser.objects.get(userId=user_id, sessionToken=session_token)
                except (TranSappUser.DoesNotExist, ValidationError):
                    pass

                token_obj = Token.objects.create(phoneId=phone_id, token=hash_token, busassignment=bus_assignment,
                                                 color=self.get_random_color(), tranSappUser=transapp_user,
                                                 timeCreation=timestamp, direction=None)

                ActiveToken.objects.create(timeStamp=timestamp, token=token_obj)
                # add current position for tokens
                if bus_longitude is not None and bus_latitude is not None:
                    PoseInTrajectoryOfToken.objects.create(timeStamp=timestamp, token=token_obj,
                                                           inVehicleOrNot=PoseInTrajectoryOfToken.IN_VEHICLE,
                                                           longitude=float(bus_longitude), latitude=float(bus_latitude))
                # we store the active token
                response["token"] = hash_token
                Status.getJsonStatus(Status.OK, response)
        except IntegrityError as e:
            logger = logging.getLogger(__name__)
            logger.error(e.message)
            Status.getJsonStatus(Status.TRIP_TOKEN_COULD_NOT_BE_CREATED, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def get_random_color(self):
        # color used by web page that shows trip trajectories
        # unused -> letters = '0123456789ABCDEF0'
        colors = {'#2c7fb8', '#dd1c77', '#016c59', '#de2d26', '#d95f0e'}
        color = list(colors)[int(round(random() * 4))]
        return color
