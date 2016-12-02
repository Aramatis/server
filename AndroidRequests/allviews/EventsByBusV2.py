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

    def get(self, request, pUuid):
        """The UUID field can identify the bus, and the service can identify
        the bus assignment"""
        logger = logging.getLogger(__name__)

        response = {}
        # response['registrationPlate'] = pRegistrationPlate
        response['uuid'] = pUuid

        try:
            bus = Busv2.objects.get(uuid=pUuid)
            pRegistrationPlate = bus.registrationPlate
            assignments = Busassignment.objects.filter(uuid=bus)
            events = self.getEventsForBus(assignments)
        except Exception as e:
            logger.error(str(e))
            events = []
            pRegistrationPlate = ''

        response['registrationPlate'] = pRegistrationPlate
        response['events'] = events

        return JsonResponse(response, safe=False)

    def getEventsForBus(self, pBusassignments):
        """this method look for the active events of a bus, those whose lifespan hasn't expired
        since the last time there were reported"""
        events = []

        eventsToAsk = Event.objects.filter(eventType='bus')

        for event in eventsToAsk:
            eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)

            registry = EventForBusv2.objects.filter(
                busassignment__in=pBusassignments,
                event=event,
                timeStamp__gt=eventTime).order_by('-timeStamp')

            # checks if the event is active
            if registry.exists():
                newEvent = registry[0].getDictionary()
                for it in registry[1:]:
                    otherEvent = it.getDictionary()
                    newEvent['eventConfirm'] = newEvent[
                        'eventConfirm'] + otherEvent['eventConfirm']
                    newEvent['eventDecline'] = newEvent[
                        'eventDecline'] + otherEvent['eventDecline']
                events.append(newEvent)
        return events
