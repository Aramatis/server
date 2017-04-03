from django.views.generic import View
from django.utils import timezone
from django.conf import settings

# my stuff
# import DB's models
from AndroidRequests.models import Event, BusStop, EventForBusStop, StadisticDataFromRegistrationBusStop

from EventsByBusStop import EventsByBusStop


class RegisterEventBusStop(View):
    '''This class handles the requests that report events of a bus stop'''

    def get(
            self,
            request,
            pUserId,
            stopCode,
            pEventID,
            pConfirmDecline,
            pLatitud=500,
            pLongitud=500):

        theEvent = Event.objects.get(id=pEventID)

        aTimeStamp = timezone.now()

        oldestAlertedTime = aTimeStamp - \
            timezone.timedelta(minutes=theEvent.lifespam)

        if EventForBusStop.objects.filter(
                timeStamp__gt=oldestAlertedTime,
                stopCode=stopCode,
                event=theEvent).exists():
            eventsReport = EventForBusStop.objects.filter(
                timeStamp__gt=oldestAlertedTime, stopCode=stopCode, event=theEvent)
            eventReport = self.getLastEvent(eventsReport)
            # updates to the event reported
            eventReport.timeStamp = aTimeStamp
            if pConfirmDecline == 'decline':
                eventReport.eventDecline += 1
            else:
                eventReport.eventConfirm += 1

            eventReport.save()

            StadisticDataFromRegistrationBusStop.objects.create(
                timeStamp=aTimeStamp,
                confirmDecline=pConfirmDecline,
                reportOfEvent=eventReport,
                longitud=pLongitud,
                latitud=pLatitud,
                userId=pUserId)
        else:
            aEventReport = EventForBusStop.objects.create(
                stopCode=stopCode,
                event=theEvent,
                timeStamp=aTimeStamp,
                timeCreation=aTimeStamp,
                userId=pUserId)

            if pConfirmDecline == 'decline':
                aEventReport.eventDecline = 1
                aEventReport.eventConfirm = 0

            aEventReport.save()

            StadisticDataFromRegistrationBusStop.objects.create(
                timeStamp=aTimeStamp,
                confirmDecline=pConfirmDecline,
                reportOfEvent=aEventReport,
                longitud=pLongitud,
                latitud=pLatitud,
                userId=pUserId)

        # Returns updated event list for a busstop
        eventsByBusStop = EventsByBusStop()
        return eventsByBusStop.get(request, stopCode)

    def getLastEvent(self, querySet):
        toReturn = querySet[0]

        for val in range(len(querySet) - 1):
            if toReturn.timeStamp < val.timeStamp:
                toReturn = val

        return toReturn
