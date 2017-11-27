from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.models import ServicesByBusStop
from AndroidRequests.encoder import TranSappJSONEncoder


class BusStopsByService(View):
    """This class handles requests for the list of bus stops for an specific service."""

    def get(self, request, route):
        """it receive the bus Service to get all the bus stops where it service stops."""
        response = {'service': route}

        # ask for the bus stops for this service
        bus_stops = self.get_bus_stops_for_route(route)

        response['paraderos'] = bus_stops

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def get_bus_stops_for_route(self, route):
        """this method look for all the bus stops where the service stops."""
        bus_stops = []

        for sbs in ServicesByBusStop.objects.filter(service=route, gtfs__version=settings.GTFS_VERSION):
            data = {}
            bus_stop = sbs.busStop
            data['codigo'] = bus_stop.code
            data['nombre'] = bus_stop.name
            data['latitud'] = bus_stop.latitude
            data['longitud'] = bus_stop.longitude
            data['eventos'] = EventsByBusStop().get_events_for_stop(
                bus_stop, timezone.now())
            bus_stops.append(data)

        return bus_stops
