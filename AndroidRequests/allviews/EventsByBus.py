from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from AndroidRequests.models import Busv2, Busassignment, Event, EventForBusv2
from AndroidRequests.encoder import TranSappJSONEncoder


class EventsByBus(View):
    """This class handles requests for the registered events for an specific bus."""

    def __init__(self):
        self.context = {}

    def get(self, request, pRegistrationPlate, pBusService):
        """It's important to give the registrarion plate and the bus
        service, because one plate could have two services."""
        # remove hyphen and convert to uppercase
        pRegistrationPlate = pRegistrationPlate.replace('-', '').upper()

        response = {'registrationPlate': pRegistrationPlate, 'service': pBusService}

        try:
            # bus = Bus.objects.get(registrationPlate=pRegistrationPlate, service=pBusService)
            bus = Busv2.objects.get(registrationPlate=pRegistrationPlate)
            busassignment = Busassignment.objects.get(
                uuid=bus, service=pBusService)
            events = self.getEventForBus(busassignment)
        except:
            events = []

        response['events'] = events

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def getEventForBus(self, pBusassignment):
        """this method look for the active events of a bus, those whose lifespan hasn't expired
        since the last time there were reported"""
        events = []

        # if pBus.registrationPlate == constants.DUMMY_LICENSE_PLATE :
        #     return events

        eventsToAsk = Event.objects.filter(eventType='bus')

        for event in eventsToAsk:
            eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)

            registry = EventForBusv2.objects.filter(
                busassignment=pBusassignment,
                event=event,
                timeStamp__gt=eventTime).order_by('-timeStamp')

            # checks if the event is active
            if registry.exists():
                registry = registry[0]
                events.append(registry.getDictionary())
        return events
