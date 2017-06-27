# python utilities
import json

from django.http import JsonResponse
from django.utils import timezone, dateparse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import AndroidRequests.scoreFunctions as score
# import DB's models
from AndroidRequests.models import ActiveToken, Token, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status


class SendPoses(View):
    """This class receives a segment of the trajectory associated to a token."""

    def __init__(self):
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
                aToken = ActiveToken.objects.get(token__token=pToken)
                aToken.timeStamp = timezone.now()
                aToken.save()

                theToken = Token.objects.get(token=pToken)
                
                for pose in trajectory:
                    # set awareness to time stamp, to the server UTC
                    aTimeStamp = dateparse.parse_datetime(pose['timeStamp'])
                    aTimeStamp = timezone.make_aware(aTimeStamp)

                    PoseInTrajectoryOfToken.objects.create(
                        longitude=pose['longitud'],
                        latitude=pose['latitud'],
                        timeStamp=aTimeStamp,
                        inVehicleOrNot=pose["inVehicleOrNot"],
                        token=theToken)

                # update score
                EVENT_ID = 'evn00300'
                metaData = {'poses': trajectory, 'tripToken': pToken}
                jsonScoreResponse = score.calculateDistanceScore(request, EVENT_ID, metaData)
                response["gamificationData"] = jsonScoreResponse
   
                Status.getJsonStatus(Status.OK, response)
            else:  # if the token was not found alert
                Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, response)

        return JsonResponse(response, safe=False)
