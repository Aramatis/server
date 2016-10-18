from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

# my stuff
# import DB's models
from AndroidRequests.models import Busv2, Event, EventForBusv2, Busassignment
# constants
import AndroidRequests.constants as Constants

class EventsByBusV2(View):
    """This class handles requests for the registered events for an specific bus."""
    def __init__(self):
        self.context={}

    def get(self, request, pUuid, pBusService):
        """The UUID field can identify the bus, and the service can identify
        the bus assignment"""
        # remove hyphen and convert to uppercase
        #pRegistrationPlate = pRegistrationPlate.replace('-', '').upper()

        response = {}
        #response['registrationPlate'] = pRegistrationPlate
        response['service'] = pBusService
        response['uuid'] = pUuid

        try:
            bus = Busv2.objects.get(uuid=pUuid)
            assignment = Busassignment.objects.get(service=pBusService, uuid=bus)
            events = self.getEventForBus(assignment) 
            pRegistrationPlate = bus.registrationPlate            
                
        except:
            events = {}
            pRegistrationPlate = ''

        response['registrationPlate'] = pRegistrationPlate
        response['events'] = events

        
        return JsonResponse(response, safe=False)

    def getEventForBus(self,pBusassignment):
        """this method look for the active events of a bus, those whose lifespan hasn't expired
        since the last time there were reported"""
        events = []

        # if pBus.registrationPlate == Constants.DUMMY_LICENSE_PLATE :
            
        #     return events

        eventsToAsk = Event.objects.filter(eventType='bus')

        for event in eventsToAsk:
            eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)

            registry = EventForBusv2.objects.filter(busassignment = pBusassignment, event=event,timeStamp__gt=eventTime).order_by('-timeStamp')

            #checks if the event is active
            if registry.exists():
                registry = registry[0]
                events.append(registry.getDictionary())
        return events
