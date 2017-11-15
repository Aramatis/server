from django.http import JsonResponse
from django.utils import timezone, dateparse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import ActiveToken, Token, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.scoreFunctions as score
import json


class SendPoses(View):
    """This class receives a segment of the trajectory associated to a token."""

    def __init__(self):
        super(SendPoses, self).__init__()
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SendPoses, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        response = {}

        if request.method == 'POST':
            pToken = request.POST.get('pToken', '')
            pTrajectory = request.POST.get('pTrajectory', '')

            if ActiveToken.objects.filter(token__token=pToken).exists():
                trajectory = json.loads(pTrajectory)
                trajectory = trajectory['poses']

                # update the token time stamp, for maintanence purpuses
                activeToken = ActiveToken.objects.select_related("token").get(token__token=pToken)
                activeToken.timeStamp = timezone.now()
                activeToken.save()

                positions = []
                for pose in trajectory:
                    # set awareness to time stamp, to the server UTC
                    aTimeStamp = dateparse.parse_datetime(pose['timeStamp'])
                    aTimeStamp = timezone.make_aware(aTimeStamp)

                    position = PoseInTrajectoryOfToken(
                        longitude=pose['longitud'],
                        latitude=pose['latitud'],
                        timeStamp=aTimeStamp,
                        inVehicleOrNot=pose["inVehicleOrNot"],
                        token=activeToken.token)
                    positions.append(position)
                PoseInTrajectoryOfToken.objects.bulk_create(positions)

                # update score
                EVENT_ID = 'evn00300'
                metaData = {'poses': trajectory, 'tripToken': pToken}
                jsonScoreResponse = score.calculateDistanceScore(request, EVENT_ID, metaData)
                response["gamificationData"] = jsonScoreResponse
   
                Status.getJsonStatus(Status.OK, response)
            else:  # if the token was not found alert
                Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
