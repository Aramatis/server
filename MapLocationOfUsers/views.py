# usefull packages from django
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.utils import timezone

# models
from AndroidRequests.models import DevicePositionInTime, PoseInTrajectoryOfToken

# Create your views here.


class MapHandler(View):
    '''This class manages the map where the markers from the devices using the
    application are shown'''

    def __init__(self):
        """the contructor, context are the parameter given to the html template"""
        self.context = {}

    def get(self, request):
        template = "map.html"

        return render(request, template, self.context)


class GetMapPositions(View):
    '''This class requests to the database the values of the actives users'''

    def __init__(self):
        """the contructor, context are the parameter given to the html template"""
        self.context = {}

    def get(self, request):

        now = timezone.now()
        earlier = now - timezone.timedelta(minutes=5)

        # the position of interest are the ones ocurred in the last 10 minutes
        postions = DevicePositionInTime.objects.filter(timeStamp__range=(earlier, now))\
            .order_by('-timeStamp')

        # TODO: get unique users from query and not fiter here
        response = []
        phones = []
        for aPosition in postions:
            if not (aPosition.phoneId in phones):
                response.append({'latitud': aPosition.latitude,
                                 'longitud': aPosition.longitude})
                phones.append(aPosition.phoneId)

        return JsonResponse(response, safe=False)


class GetMapTrajectory(View):
    """This class handles the requests for getting the Trajectory of some tokens that where
    updated in the last 10 minutes"""

    def __init__(self):
        """the contructor, context are the parameter given to the html template"""
        self.context = {}

    def get(self, request):

        tokens = self.getTokenUsedIn10LastMinutes()
        response = []

        for aToken in tokens:
            tokenResponse = {}
            trajectory = PoseInTrajectoryOfToken.objects.filter(
                token=aToken, inVehicleOrNot="vehicle").order_by('-timeStamp')

            aPose = trajectory[0]

            tokenResponse['lastPose'] = (aPose.latitude, aPose.longitude)
            tokenResponse['token'] = aToken.token
            tokenResponse['myColor'] = aToken.color
            response.append(tokenResponse)

        return JsonResponse(response, safe=False)

    def getTokenUsedIn10LastMinutes(self):
        '''return the tokens that have the latest entry at least 5 minutes ago'''
        now = timezone.now()

        earlier = now - timezone.timedelta(minutes=5)
        allPoses = PoseInTrajectoryOfToken.objects.filter(
            timeStamp__range=(earlier, now))

        tokens = []

        for aPose in allPoses:
            if aPose.token not in tokens:
                tokens.append(aPose.token)

        return tokens
