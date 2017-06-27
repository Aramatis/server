from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
# import DB's models
from AndroidRequests.models import ServicesByBusStop


class BusStopsByService(View):
    """This class handles requests for the list of bus stops for an specific service."""

    def __init__(self):
        self.context = {}

    def get(self, request, pBusService):
        """it receive the bus Service to get all the bus stops where it service stops."""
        response = {'service': pBusService}

        # ask for the bus stops for this service
        busStops = self.getBusStopsForService(pBusService)

        response['paraderos'] = busStops

        return JsonResponse(response, safe=False)

    def getBusStopsForService(self, pBusService):
        """this method look for all the bus stops where the service stops."""
        busStops = []

        for sbs in ServicesByBusStop.objects.filter(service=pBusService, gtfs__version=settings.GTFS_VERSION):
            data = {}
            busStop = sbs.busStop
            data['codigo'] = busStop.code
            data['nombre'] = busStop.name
            data['latitud'] = busStop.latitude
            data['longitud'] = busStop.longitude
            getEventsByBusStop = EventsByBusStop()
            data['eventos'] = getEventsByBusStop.getEventsForStop(
                busStop, timezone.now())
            busStops.append(data)

        return busStops
