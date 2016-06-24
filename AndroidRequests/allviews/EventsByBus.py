from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

#python utilities
import requests
# my stuff
# import DB's models
from AndroidRequests.models import *

class EventsByBus(View):
    """This class handles requests for the registered events for an specific bus."""
    def __init__(self):
        self.context={}

    def get(self, request, pRegistrationPlate,pBusService):
        """It's important to give the registrarion plate and the bus
        service, because one plate could have two services."""
        response = {}
        bus = Bus.objects.get(registrationPlate=pRegistrationPlate, service=pBusService)
        response['registrationPlate'] = pRegistrationPlate
        response['service'] = bus.service

        # ask for the events in this bus
        events = self.getEventForBus(bus)

        response['events'] = events

        return JsonResponse(response, safe=False)

    def getEventForBus(self,pBus):
        """this method look for the active events of a bus, those whose lifespan hasn't expired
        since the last time there were reported"""
        events = []

        eventsToAsk = Event.objects.filter(eventType='bus')

        for event in eventsToAsk:
            eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)

            registry = EventForBus.objects.filter(bus = pBus, event=event,timeStamp__gt=eventTime).order_by('-timeStamp')

            #checks if the event is active
            if registry.exists():
                registry = registry[0]
                events.append(registry.getDictionary())
        return events
