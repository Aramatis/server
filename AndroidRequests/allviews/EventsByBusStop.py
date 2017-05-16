from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone
from django.conf import settings
from django.db.models.expressions import F

# my stuff
# import DB's models
from AndroidRequests.models import BusStop, Event, EventForBusStop


class EventsByBusStop(View):
    """This class handles requests for the current reported events
    for a given bus stop."""

    def get(self, resquest, stopCode):
        """Only the bus stop code is needed."""

        timestamp = timezone.now()
        stopObj = BusStop.objects.get(code=stopCode, gtfs__version=settings.GTFS_VERSION)

        # ask for the events
        eventsData = self.getEventsForStop(stopCode, timestamp)

        eventDictionary = stopObj.getDictionary()
        eventDictionary['events'] = eventsData

        return JsonResponse(eventDictionary, safe=False)

    def getEventsForStop(self, stopCode, timeStamp):
        '''this method returns all the events that are active given their timestamp.'''

        currentEventReport = []

        # ask for events that ocured between now and the lifeSpam of it
        events = EventForBusStop.objects.prefetch_related('stadisticdatafromregistrationbusstop_set').filter(
            stopCode=stopCode, event__eventType='busStop', broken=False,
            expireTime__gte=timeStamp, timeCreation__lte=timeStamp).order_by('-timeStamp')
        
        for event in events:
            currentEventReport.append(event.getDictionary())
        
        return currentEventReport
