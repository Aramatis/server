from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone
from django.conf import settings

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

        eventeDictionary = stopObj.getDictionary()
        eventeDictionary['events'] = eventsData

        return JsonResponse(eventeDictionary, safe=False)

    def getEventsForStop(self, stopCode, timeStamp):
        '''this method returns all the events that are active given their timestamp.'''

        currentEventReport = []

        events = Event.objects.filter(eventType='busStop')

        # this will discart all the events that have expired
        for event in events:
            eventTime = timeStamp - timezone.timedelta(minutes=event.lifespam)
            # ask for events that ocured between now and the lifeSpam of it
            aux = EventForBusStop.objects.filter(
                stopCode=stopCode, event=event, timeStamp__gt=eventTime).order_by('-timeStamp')

            # check if there exist one event that fit descritions and
            if aux.exists():
                # add the add the info as a dictionry to a list of events
                currentEventReport.append(aux[0].getDictionary())

        return currentEventReport
