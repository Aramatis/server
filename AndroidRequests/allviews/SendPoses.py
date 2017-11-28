from django.http import JsonResponse
from django.utils import timezone, dateparse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from AndroidRequests.models import ActiveToken, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.scoreFunctions as score
import json


class SendPoses(View):
    """This class receives a segment of the trajectory associated to a token."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SendPoses, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        response = {}

        token = request.POST.get('pToken', '')
        trajectory = request.POST.get('pTrajectory', '')

        if ActiveToken.objects.filter(token__token=token).exists():
            trajectory = json.loads(trajectory)
            trajectory = trajectory['poses']

            if len(trajectory) > 0:
                # update the token time stamp, for maintanence purpuses
                active_token = ActiveToken.objects.select_related("token").get(token__token=token)
                active_token.timeStamp = timezone.now()
                active_token.save()

                positions = []
                tuple_list = []

                for pose in trajectory:
                    # set awareness to time stamp, to the server UTC
                    timestamp = dateparse.parse_datetime(pose['timeStamp'])
                    timestamp = timezone.make_aware(timestamp)

                    position = PoseInTrajectoryOfToken(
                        longitude=pose['longitud'],
                        latitude=pose['latitud'],
                        timeStamp=timestamp,
                        inVehicleOrNot=pose["inVehicleOrNot"],
                        token=active_token.token)
                    positions.append(position)
                    tuple_list.append((pose['longitud'], pose['latitud'], timestamp))
                PoseInTrajectoryOfToken.objects.bulk_create(positions)

                # update score
                event_id = 'evn00300'
                meta_data = {
                    'poses': tuple_list,
                    'token': token
                }
                json_score_response = score.calculate_distance_score(request, event_id, meta_data)
                response["gamificationData"] = json_score_response

                Status.getJsonStatus(Status.OK, response)
            else:
                Status.getJsonStatus(Status.TRAJECTORY_DOES_NOT_HAVE_LOCATIONS, response)
        else:  # if the token was not found alert
            Status.getJsonStatus(Status.TRIP_TOKEN_DOES_NOT_EXIST, response)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
