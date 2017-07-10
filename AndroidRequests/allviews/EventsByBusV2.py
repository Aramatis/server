import logging

from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from collections import defaultdict

# my stuff
# import DB's models
from AndroidRequests.models import Busv2, EventForBusv2, Busassignment


class EventsByBusV2(View):
    """This class handles requests for the registered events for an specific bus."""

    def __init__(self):
        self.context = {}
        self.logger = logging.getLogger(__name__)

    def get(self, request, pPhoneId):
        """The UUID field can identify the bus, and the service can identify
        the bus assignment"""

        response = {'uuid': pPhoneId}
        # response['registrationPlate'] = pRegistrationPlate

        try:
            bus = Busv2.objects.get(uuid=pPhoneId)
            pRegistrationPlate = bus.registrationPlate
            assignments = Busassignment.objects.filter(uuid=bus)
            events = self.getEventsForBuses(assignments, timezone.now())[bus.uuid]
        except Exception as e:
            self.logger.error(str(e))
            events = []
            pRegistrationPlate = ''

        response['registrationPlate'] = pRegistrationPlate
        response['events'] = events

        return JsonResponse(response, safe=False)

    def getEventsForBuses(self, busassignments, timeStamp):
        """ this method get events of group of buses with one hit to database """

        events = EventForBusv2.objects.prefetch_related('stadisticdatafromregistrationbus_set__tranSappUser',
                                                        'busassignment__uuid',
                                                        'busassignment__events').filter(
            busassignment__in=busassignments, event__eventType='bus', broken=False,
            expireTime__gte=timeStamp, timeCreation__lte=timeStamp).order_by('-timeStamp')

        eventsByMachineId = defaultdict(list)
        for event in events:
            eventsByMachineId[event.busassignment.uuid.uuid].append(event)

        eventListByBus = defaultdict(None)
        for machineId, events in eventsByMachineId.iteritems():
            aggregatedEvents = {}
            result = []
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
            eventListByBus[machineId] = result

        return eventListByBus
