from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from AndroidRequests.models import BusStop, EventForBusStop
from AndroidRequests.encoder import TranSappJSONEncoder


class EventsByBusStop(View):
    """This class handles requests for the current reported events
    for a given bus stop."""

    def get(self, request, stop_code):
        """Only the bus stop code is needed."""

        timestamp = timezone.now()
        stop_obj = BusStop.objects.get(code=stop_code, gtfs__version=settings.GTFS_VERSION)

        event_dictionary = stop_obj.getDictionary()
        event_dictionary['events'] = self.getEventsForStop(stop_code, timestamp)

        return JsonResponse(event_dictionary, safe=False, encoder=TranSappJSONEncoder)

    def getEventsForStop(self, stop_code, timestamp):
        """this method returns all the events that are active given their timestamp."""

        current_event_report = []

        # ask for events that ocured between now and the lifeSpam of it
        events = EventForBusStop.objects.prefetch_related('stadisticdatafromregistrationbusstop_set__tranSappUser',
                                                          'event'). \
            filter(stopCode=stop_code, event__eventType='busStop', broken=False,
                   expireTime__gte=timestamp, timeCreation__lte=timestamp).order_by('-timeStamp')

        for event in events:
            current_event_report.append(event.getDictionary())

        return current_event_report
