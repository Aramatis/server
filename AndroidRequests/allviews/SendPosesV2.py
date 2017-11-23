from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import ActiveToken, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

from onlinegps import views as onlinepgsview

import AndroidRequests.scoreFunctions as score
import AndroidRequests.constants as constants
import json


class SendPosesV2(View):
    """ This class receives a segment of the trajectory associated to a token. """

    def __init__(self):
        super(SendPosesV2, self).__init__()
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SendPosesV2, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        response = {}

        token = request.POST.get('token')
        trajectory = request.POST.get('trajectory')

        if ActiveToken.objects.filter(token__token=token).exists():
            trajectory = json.loads(trajectory)
            trajectory = trajectory["poses"]

            if len(trajectory) > 0:
                now = timezone.now()
                # update the token timestamp, to keep as active token
                activeToken = ActiveToken.objects.select_related("token__busassignment__uuid").get(token__token=token)
                activeToken.timeStamp = now
                activeToken.save()

                positions = []
                tupleList = []

                for pose in trajectory:
                    # time delay is in miliseconds
                    seconds = pose['timeDelay'] / 1000
                    currentTime = now + timezone.timedelta(seconds=seconds)

                    position = PoseInTrajectoryOfToken(longitude=pose['longitude'], latitude=pose['latitude'],
                                                       timeStamp=currentTime, inVehicleOrNot=pose["inVehicleOrNot"],
                                                       token=activeToken.token)
                    positions.append(position)
                    tupleList.append((pose['longitude'], pose['latitude'], currentTime))
                PoseInTrajectoryOfToken.objects.bulk_create(positions)

                # update score
                EVENT_ID = 'evn00300'
                metaData = {
                    'poses': tupleList,
                    'token': token,
                }
                jsonScoreResponse = score.calculateDistanceScore(request, EVENT_ID, metaData)
                response["gamificationData"] = jsonScoreResponse

                # check with real bus
                licensePlate = activeToken.token.busassignment.uuid.registrationPlate
                if licensePlate == constants.DUMMY_LICENSE_PLATE:
                    Status.getJsonStatus(Status.I_DO_NOT_KNOW_ANYTHING_ABOUT_REAL_BUS, response)
                else:
                    locations = PoseInTrajectoryOfToken.objects.filter(
                        timeStamp__gt=now - timezone.timedelta(minutes=2)).values_list("longitude", "latitude",
                                                                                       "timeStamp")
                    is_near_to_real_bus = onlinepgsview.is_near_to_bus_position(licensePlate, locations)
                    if is_near_to_real_bus == onlinepgsview.GET_OFF:
                        Status.getJsonStatus(Status.USER_BUS_IS_FAR_AWAY_FROM_REAL_BUS, response)
                    elif is_near_to_real_bus == onlinepgsview.I_DO_NOT_KNOW:
                        Status.getJsonStatus(Status.I_DO_NOT_KNOW_ANYTHING_ABOUT_REAL_BUS, response)
                    else:
                        Status.getJsonStatus(Status.OK, response)
            else:
                Status.getJsonStatus(Status.TRAJECTORY_DOES_NOT_HAVE_LOCATIONS, response)
        else:  # if the token was not found alert
            Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
