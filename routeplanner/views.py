from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.generic import View

# python utilities
import requests

# third-party libraries
import googlemaps

# Create your views here.

class RoutePlanner(View):
    """
    Manage the interaction between google and TranSapp users, let them
    calculate a route to move one location to another.
    """

    def __init__(self):
        self.context={}

    def get(self, request):
        """
        Method to calculate a route between two locations
        You can learn more about this here ->
        https://developers.google.com/maps/documentation/directions/intro#TravelModes
        """

        # GET PARAMETERS

        origin = request.GET.get('origin', '')
        destination = request.GET.get('destination', '')
        language = request.GET.get('lang', 'es')
        #language of message given by direction API, whatever thing differect to
        # correct language, direction API return user message in english

        if origin == '' or destination == '':
            return JsonResponse([], safe = False)
        # verify that parameter exists

        googleClient = googlemaps.Client(settings.GOOGLE_KEY)

        # DIRECTION API PARAMETERS

        mode = "transit"
        """
        type of transport that user can be used:
        - driving
        - walking
        - bycycling
        - transit
            - in this option it can define a "departure_time", default is "now"
        """

        avoid = ""
        """
        places that route has to avoid:
        - tolls
        - highways
        - ferries
        """

        units = "metric"
        """
        the distance field has a text with the unit distance of the country defined,
        but you can say explicitly the units. It can be:
        - metric: kilometers and meters
        - imperial: miles and foots
        """

        region = "cl"
        """
        Region restriction. It help to google to find the correct location.
        """

        alternatives = True
        """
        it says that google can return multiples trajectories
        """

        routes = googleClient.directions(origin, destination,
                                         mode = mode,
                                         avoid = avoid,
                                         units = units,
                                         region = region,
                                         alternatives = alternatives,
                                         language = language)

        return JsonResponse(routes, safe = False)
