from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

import logging
# my stuff
# import DB's models
from AndroidRequests.models import Busv2, Event, EventForBusv2, Busassignment


class EventsByBusV2(View):
    """This class handles requests for the registered events for an specific bus."""

    def __init__(self):
        self.context = {}
        self.logger = logging.getLogger(__name__)

    def get(self, request, pPhoneId):
        """The UUID field can identify the bus, and the service can identify
        the bus assignment"""

        response = {}
        # response['registrationPlate'] = pRegistrationPlate
        response['uuid'] = pPhoneId

        try:
            bus = Busv2.objects.get(uuid=pPhoneId)
            pRegistrationPlate = bus.registrationPlate
            assignments = Busassignment.objects.filter(uuid=bus)
            events = self.getEventsForBus(assignments, timezone.now())
        except Exception as e:
            print e
            self.logger.error(str(e))
            events = []
            pRegistrationPlate = ''

        response['registrationPlate'] = pRegistrationPlate
        response['events'] = events

        return JsonResponse(response, safe=False)

    def getEventsForBus(self, busassignments, timeStamp):
        """this method look for the active events of a bus, those whose lifespan hasn't expired
        since the last time there were reported"""
        aggregatedEvents = {}
        result = []

        events = EventForBusv2.objects.prefetch_related('stadisticdatafromregistrationbus_set__tranSappUser').filter(
                busassignment__in=busassignments, event__eventType='bus', broken=False,
                expireTime__gte=timeStamp, timeCreation__lte=timeStamp).order_by('-timeStamp')
        
        for event in events:
            event = event.getDictionary()
            
            if event['eventcode'] in aggregatedEvents:
                position = aggregatedEvents[event['eventcode']]
                result[position]['eventConfirm'] += event['eventConfirm']
                result[position]['eventDecline'] += event['eventDecline']
                result[position]['confirmedVoteList'] += event['confirmedVoteList']
                result[position]['declinedVoteList'] += event['declinedVoteList']
            else:
                aggregatedEvents[event['eventcode']] = len(result)
                result.append(event)
        
        return result
