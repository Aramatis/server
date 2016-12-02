from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

# my stuff
# import DB's models
from AndroidRequests.models import BusStop, Event, EventForBusStop


class EventsByBusStop(View):
    """This class handles requests for the current reported events
    for a given bus stop."""

    def get(self, resquest, pBusStopCode):
        """Only the busto code is needed."""
        aTimeStamp = timezone.now()
        theBusStop = BusStop.objects.get(code=pBusStopCode)

        # ask for the events
        eventsData = self.getEventsForBusStop(theBusStop, aTimeStamp)

        eventeDictionary = theBusStop.getDictionary()
        eventeDictionary['events'] = eventsData

        return JsonResponse(eventeDictionary, safe=False)

    def getEventsForBusStop(self, pBusStop, pTimeStamp):
        '''this method returns all the events that are active given their timestamp.'''

        currentEventReport = []

        events = Event.objects.filter(eventType='busStop')

        # this will discart all the events that have expire
        for event in events:

            eventTime = pTimeStamp - timezone.timedelta(minutes=event.lifespam)
            # ask for events that ocured between now and the lifeSpam of it
            aux = EventForBusStop.objects.filter(
                busStop=pBusStop, event=event, timeStamp__gt=eventTime).order_by('-timeStamp')

            # check if there exist one event that fit descritions and
            if aux.exists():
                # add the add the info as a dictionry to a list of events
                currentEventReport.append(aux[0].getDictionary())

        return currentEventReport
