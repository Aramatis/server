from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

# my stuff
# import DB's models
from AndroidRequests.models import Bus, Event, EventForBus
# constants
import AndroidRequests.constants as Constants

class EventsByBus(View):
    """This class handles requests for the registered events for an specific bus."""
    def __init__(self):
        self.context={}

    def get(self, request, pRegistrationPlate,pBusService, puuid=0):
        """It's important to give the registrarion plate and the bus
        service, because one plate could have two services."""
        # remove hyphen and convert to uppercase
        pRegistrationPlate = pRegistrationPlate.replace('-', '').upper()

        response = {}
        response['registrationPlate'] = pRegistrationPlate
        response['service'] = pBusService

        try:
            if puuid != 0:
                bus = Bus.objects.get(registrationPlate=pRegistrationPlate, service=pBusService, uuid=puuid)
                events = self.getEventForBus(bus)
            elif puuid == 0 and pRegistrationPlate != Constants.DUMMY_LICENSE_PLATE:
                bus = Bus.objects.get(registrationPlate=pRegistrationPlate, service=pBusService)
                events = self.getEventForBus(bus)
            else:
                bus = Bus.objects.get(registrationPlate=pRegistrationPlate, service=pBusService)
                events = {}
        except:
            events = {}

        response['events'] = events

        return JsonResponse(response, safe=False)

    def getEventForBus(self,pBus):
        """this method look for the active events of a bus, those whose lifespan hasn't expired
        since the last time there were reported"""
        events = []

        # if pBus.registrationPlate == Constants.DUMMY_LICENSE_PLATE :
            
        #     return events

        eventsToAsk = Event.objects.filter(eventType='bus')

        for event in eventsToAsk:
            eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)

            registry = EventForBus.objects.filter(bus = pBus, event=event,timeStamp__gt=eventTime).order_by('-timeStamp')

            #checks if the event is active
            if registry.exists():
                registry = registry[0]
                events.append(registry.getDictionary())
        return events
