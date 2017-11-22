from django.http import JsonResponse
from django.utils import timezone, dateparse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import ActiveToken, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

from onlinegps.views import is_near_to_bus_position

import AndroidRequests.scoreFunctions as score
import json


class SendPosesV2(View):
    """This class receives a segment of the trajectory associated to a token."""

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
            trajectory = trajectory['poses']

            now = timezone.now()
            # update the token time stamp, for maintenance purposes
            activeToken = ActiveToken.objects.select_related("token__busassignment__uuid").get(token__token=token)
            activeToken.timeStamp = now
            activeToken.save()

            positions = []
            currentTime = now

            # first position
            firstPose = trajectory[0]
            position = PoseInTrajectoryOfToken(longitude=firstPose['longitud'], latitude=firstPose['latitud'],
                                               timeStamp=now, inVehicleOrNot=firstPose["inVehicleOrNot"],
                                               token=activeToken.token)
            positions.append(position)
            tupleList = []

            for index, pose in (reversed(trajectory[1:])):
                secondsDiff = dateparse.parse_datetime(pose['diff'])
                currentTime -= timezone.timedelta(seconds=secondsDiff)

                position = PoseInTrajectoryOfToken(longitude=pose['longitude'], latitude=pose['latitude'],
                    timeStamp=currentTime, inVehicleOrNot=pose["inVehicleOrNot"], token=activeToken.token)
                positions.append(position)
                tupleList.append((pose['longitude'], pose['latitude'], currentTime))
            PoseInTrajectoryOfToken.objects.bulk_create(positions)

            # update score
            EVENT_ID = 'evn00300'
            metaData = {'poses': trajectory, 'token': token}
            jsonScoreResponse = score.calculateDistanceScore(request, EVENT_ID, metaData)
            response["gamificationData"] = jsonScoreResponse

            # check with real bus
            licensePlate = token.busassignment.uuid.registrationPlate
            if is_near_to_bus_position(licensePlate, tupleList):
                Status.getJsonStatus(Status.USER_BUS_IS_FAR_AWAY_FROM_REAL_BUS, response)
            else:
                Status.getJsonStatus(Status.OK, response)
        else:  # if the token was not found alert
            Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
