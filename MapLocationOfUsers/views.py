from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.utils import timezone
from django.db.models.functions import TruncDay
from django.db.models import DateTimeField, Count

from AndroidRequests.models import DevicePositionInTime, PoseInTrajectoryOfToken, Token, TranSappUser
from AndroidRequests.encoder import TranSappJSONEncoder

import datetime


class MapHandler(View):
    """This class manages the map where the markers from the devices using the
    application are shown"""

    def __init__(self):
        """the contructor, context are the parameter given to the html template"""
        super(MapHandler, self).__init__()
        self.context = {}

    def get(self, request):
        template = "map.html"

        return render(request, template, self.context)


class GetMapPositions(View):
    """This class requests to the database the values of the actives users"""

    def __init__(self):
        """the contructor, context are the parameter given to the html template"""
        super(GetMapPositions, self).__init__()
        self.context = {}

    def get(self, request):
        now = timezone.now()
        earlier = now - timezone.timedelta(minutes=5)

        # the position of interest are the ones ocurred in the last 5 minutes
        positions = DevicePositionInTime.objects.filter(timeStamp__range=(earlier, now)) \
            .order_by('phoneId', '-timeStamp').distinct("phoneId")

        response = []
        for aPosition in positions:
            response.append({
                'latitud': aPosition.latitude,
                'longitud': aPosition.longitude
            })

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)


class GetMapTrajectory(View):
    """This class handles the requests for getting the Trajectory of some tokens that where
    updated in the last 10 minutes"""

    def __init__(self):
        """the contructor, context are the parameter given to the html template"""
        super(GetMapTrajectory, self).__init__()
        self.context = {}

    def get(self, request):

        tokens = self.getTokenUsedIn5LastMinutes()
        response = []

        for aToken in tokens:
            tokenResponse = {}
            trajectory = PoseInTrajectoryOfToken.objects.filter(
                token__token=aToken[0], inVehicleOrNot=PoseInTrajectoryOfToken.IN_VEHICLE).order_by('-timeStamp')

            if len(trajectory) == 0:
                continue

            aPose = trajectory[0]

            tokenResponse['lastPose'] = (aPose.latitude, aPose.longitude)
            tokenResponse['token'] = aToken[0]
            tokenResponse['myColor'] = aToken[1]
            response.append(tokenResponse)

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def getTokenUsedIn5LastMinutes(self):
        """return the tokens that have the latest entry at least 5 minutes ago"""
        now = timezone.now()

        earlier = now - timezone.timedelta(minutes=5)
        allPoses = PoseInTrajectoryOfToken.objects.filter(
            timeStamp__range=(earlier, now)).values_list("token_id", flat=True)
        tokens = Token.objects.filter(id__in=allPoses).values_list("token", "color")

        return tokens

class GetGamificationUsersByDay(View):

    def __init__(self):
        """the contructor, context are the parameter given to the html template"""
        super(GetGamificationUsersByDay, self).__init__()
        self.context = {}

    def get(self, request):
        newUsersByDay = list(TranSappUser.objects.annotate(
            day=TruncDay("timeCreation", output_field=DateTimeField())).\
            values('day').annotate(users=Count('id')).order_by("timeCreation"))

        days = []
        if len(newUsersByDay) > 0:
            firstDay = newUsersByDay[0]["day"]
            endDay = newUsersByDay[-1]["day"] + datetime.timedelta(days=1)
            day = firstDay
            day_index = 0
            while day != endDay:
                users = 0
                if day == newUsersByDay[day_index]["day"]:
                    users = newUsersByDay[day_index]["users"]
                    day_index += 1
                days.append({
                    "day": day,
                    "users": users
                })
                day = day + datetime.timedelta(days=1)

        response = {
            "usersByDay": days
        }
        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
