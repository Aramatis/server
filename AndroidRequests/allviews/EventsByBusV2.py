import logging

from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from collections import defaultdict

from AndroidRequests.models import Busv2, EventForBusv2, Busassignment
from AndroidRequests.encoder import TranSappJSONEncoder


class EventsByBusV2(View):
    """This class handles requests for the registered events for an specific bus."""

    def __init__(self):
        super(EventsByBusV2, self).__init__()
        self.logger = logging.getLogger(__name__)

    def get(self, request, machine_id):
        """The UUID field can identify the bus, and the service can identify
        the bus assignment"""

        response = {'uuid': machine_id}
        # response['registrationPlate'] = pRegistrationPlate

        try:
            bus = Busv2.objects.get(uuid=machine_id)
            license_plate = bus.registrationPlate
            bus_assignments = Busassignment.objects.filter(uuid=bus)
            events = self.get_events_for_buses(bus_assignments, timezone.now())[bus.uuid]
        except (Busv2.DoesNotExist, KeyError) as e:
            # is related with uuid does not have events
            self.logger.error(str(e))
            events = []
            license_plate = ''

        response['registrationPlate'] = license_plate
        response['events'] = events

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)

    def get_events_for_buses(self, bus_assignments, timestamp):
        """ this method get events of group of buses with one hit to database """

        events = EventForBusv2.objects.prefetch_related('stadisticdatafromregistrationbus_set__tranSappUser',
                                                        'busassignment__uuid',
                                                        'busassignment__events').filter(
            busassignment__in=bus_assignments, event__eventType='bus', broken=False,
            expireTime__gte=timestamp, timeCreation__lte=timestamp).order_by('-timeStamp')

        events_by_machine_id = defaultdict(list)
        for event in events:
            events_by_machine_id[event.busassignment.uuid.uuid].append(event)

        event_list_by_bus = defaultdict(None)
        for machine_id, events in events_by_machine_id.iteritems():
            aggregated_events = {}
            result = []
            for event in events:
                event = event.getDictionary()

                if event['eventcode'] in aggregated_events:
                    position = aggregated_events[event['eventcode']]
                    result[position]['eventConfirm'] += event['eventConfirm']
                    result[position]['eventDecline'] += event['eventDecline']
                    result[position]['confirmedVoteList'] += event['confirmedVoteList']
                    result[position]['declinedVoteList'] += event['declinedVoteList']
                else:
                    aggregated_events[event['eventcode']] = len(result)
                    result.append(event)
            event_list_by_bus[machine_id] = result

        return event_list_by_bus
