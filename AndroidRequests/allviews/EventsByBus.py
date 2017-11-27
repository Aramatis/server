from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from AndroidRequests.models import Busv2, Busassignment, Event, EventForBusv2
from AndroidRequests.encoder import TranSappJSONEncoder


class EventsByBus(View):
    """This class handles requests for the registered events for an specific bus."""

    def get(self, request, license_plate, route):
        """It's important to give the registrarion plate and the bus
        service, because one plate could have two services."""
        # remove hyphen and convert to uppercase
        license_plate = license_plate.replace('-', '').upper()

        response = {'registrationPlate': license_plate, 'service': route}

        try:
            bus = Busv2.objects.get(registrationPlate=license_plate)
            bus_assignment = Busassignment.objects.get(
                uuid=bus, service=route)
            events = self.get_event_for_bus(bus_assignment)
        except Busv2.DoesNotExist:
            events = []

        response['events'] = events

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def get_event_for_bus(self, bus_assignment):
        """this method look for the active events of a bus, those whose lifespan hasn't expired
        since the last time there were reported"""
        events = []

        # if pBus.registrationPlate == constants.DUMMY_LICENSE_PLATE :
        #     return events

        events_to_ask = Event.objects.filter(eventType=Event.BUS_TYPE)

        for event in events_to_ask:
            event_time = timezone.now() - timezone.timedelta(minutes=event.lifespam)

            registry = EventForBusv2.objects.filter(
                busassignment=bus_assignment,
                event=event,
                timeStamp__gt=event_time).order_by('-timeStamp')

            # checks if the event is active
            if registry.exists():
                registry = registry[0]
                events.append(registry.get_dictionary())
        return events
