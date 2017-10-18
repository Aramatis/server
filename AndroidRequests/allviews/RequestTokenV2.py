from random import random

from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError

from AndroidRequests.models import Busv2, Busassignment, Token, ActiveToken, TranSappUser, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

import hashlib
import os
import logging


class RequestTokenV2(View):
    """This class handles the start of the tracking, assigning a token
    to identify the trip, not the device."""

    def __init__(self):
        super(RequestTokenV2, self).__init__()
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
        # current bus position
        busLatitude = request.POST.get('latitude')
        busLongitude = request.POST.get('longitude')

        return self.get(request, phoneId, route, machineId, busLatitude, busLongitude, userId, sessionToken)

    def get(self, request, pPhoneId, pBusService, pUUID, busLatitude=None, busLongitude=None,
            userId=None, sessionToken=None, timeStamp=None):
        """  """

        if timeStamp is None:
            timeStamp = timezone.now()
        salt = os.urandom(20)
        hashToken = hashlib.sha512(str(timeStamp) + salt).hexdigest()
        # the token is primary a hash of the time stamp plus a random salt

        response = {}
        try:
            with transaction.atomic():
                busV2 = Busv2.objects.get(uuid=pUUID)
                busAssignment = Busassignment.objects.get_or_create(uuid=busV2, service=pBusService)[0]

                tranSappUser = None
                try:
                    tranSappUser = TranSappUser.objects.get(userId=userId, sessionToken=sessionToken)
                except Exception:
                    pass

                tokenObj = Token.objects.create(phoneId=pPhoneId, token=hashToken, busassignment=busAssignment,
                    color=self.getRandomColor(), tranSappUser=tranSappUser, timeCreation=timeStamp, direction=None)

                ActiveToken.objects.create(timeStamp=timeStamp, token=tokenObj)
                # add current position for tokens
                if busLongitude is not None and busLatitude is not None:
                    PoseInTrajectoryOfToken.objects.create(timeStamp=timeStamp, token=tokenObj,
                                                           inVehicleOrNot=PoseInTrajectoryOfToken.IN_VEHICLE,
                                                           longitude=float(busLongitude), latitude=float(busLatitude))
                # we store the active token
                response["token"] = hashToken
                Status.getJsonStatus(Status.OK, response)
        except IntegrityError as e:
            logger = logging.getLogger(__name__)
            logger.error(e.message(), e.args)
            Status.getJsonStatus(Status.TRIP_TOKEN_COULD_NOT_BE_CREATED, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def getRandomColor(self):
        # color used by web page that shows trip trajectories
        # unused -> letters = '0123456789ABCDEF0'
        colors = {'#2c7fb8', '#dd1c77', '#016c59', '#de2d26', '#d95f0e'}
        color = list(colors)[int(round(random() * 4))]
        return color
