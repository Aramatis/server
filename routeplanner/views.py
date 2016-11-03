from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.generic import View

# python utilities
import requests
import logging

# third-party libraries
import googlemaps
from routeplanner.models import Log

# Create your views here.

class RoutePlanner(View):
    """
    Manage the interaction between google and TranSapp users, let them
    calculate a route to move from one location to another.
    """

    def __init__(self):
        self.context = {}

    def get(self, request, pUserId, pOrigin, pDestination, language = "es"):
        """
        Method to calculate a route between two locations
        You can learn more about this here ->
        https://developers.google.com/maps/documentation/directions/intro#TravelModes
        """

        # Log 
        Log.objects.create(userId = pUserId, origin = pOrigin, destination = pDestination)
     
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

        transitMode = ["bus", "rail"]
        """
        Specifies one or more preferred modes of transit. This parameter may only be
        specified for requests where the mode is transit. Valid values are:
        "bus", "subway", "train", "tram", "rail"
        "rail" is equivalent to ["train, "tram", "subway"]
        """

        #transitRoutingPreference = "less_walking"
        """
        Specifies preferences for transit requests. Valid values are "less_walking" or
        "fewer_transfers"
        """

        #departureTime =
        """ Specifies the desired time of departure. Default: Now """

        #arrivalTime =
        """
        Specifies the desired time of arrival for transit directions.
        Note: you can't specify both departure_time and arrival_time
        """

        avoid = []
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

        try:
            routes = googleClient.directions(pOrigin, pDestination,
                                             mode = mode,
                                             transit_mode = transitMode,
                                             #transit_routing_preference = transitRoutingPreference,
                                             avoid = avoid,
                                             units = units,
                                             region = region,
                                             alternatives = alternatives,
                                             language = language)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(str(e))
            routes = []

        return JsonResponse(routes, safe = False)
