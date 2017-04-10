from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

# my stuff
# import DB's models
from AndroidRequests.models import Event, Busv2, Busassignment, EventForBusv2, StadisticDataFromRegistrationBus

import AndroidRequests.constants as Constants

from EventsByBusV2 import EventsByBusV2
import AndroidRequests.gpsFunctions as Gps


class RegisterEventBus(View):
    '''This class handles requests that report events of a bus.'''

    def get(
            self,
            request,
            pPhoneId,
            pBusService,
            pBusPlate,
            pEventID,
            pConfirmDecline,
            pLatitud=500,
            pLongitud=500):
        # here we request all the info needed to proceed
        aTimeStamp = timezone.now()
        theEvent = Event.objects.get(id=pEventID)

        # remove hyphen and convert to uppercase
        pBusPlate = pBusPlate.replace('-', '').upper()

        if pBusPlate == Constants.DUMMY_LICENSE_PLATE:
            response = {}
            events = []
            dictionary = {}

            response['registrationPlate'] = pBusPlate
            response['service'] = pBusService

            dictionary['eventConfirm'] = 1
            dictionary['eventDecline'] = 0
            creation = timezone.localtime(timezone.now())
            stamp = timezone.localtime(timezone.now())
            dictionary['timeCreation'] = creation.strftime("%d-%m-%Y %H:%M:%S")
            dictionary['timeStamp'] = stamp.strftime("%d-%m-%Y %H:%M:%S")
            eventDictionary = theEvent.getDictionary()
            dictionary.update(eventDictionary)

            events.append(dictionary)
            # events[0].
            response['events'] = events
            return JsonResponse(response, safe=False)
            # TODO
            # Problem: there is no way to identify THE dummy bus without the uuid.
            # Return the same event.
        else:
            theBus = Busv2.objects.get_or_create(
                registrationPlate=pBusPlate)[0]
            theAssignment = Busassignment.objects.get(
                service=pBusService, uuid=theBus)
        # estimate the oldest time where the reported event can be usefull
        # if there is no event here a new one is created
        oldestAlertedTime = aTimeStamp - \
            timezone.timedelta(minutes=theEvent.lifespam)

        # get the GPS data from the url
        responseLongitud = None
        responseLatitud = None
        responseTimeStamp = None
        responseDistance = None

        responseLongitud, responseLatitud, responseTimeStamp, responseDistance = Gps.getGPSData(
            theBus.registrationPlate, aTimeStamp, float(pLongitud), float(pLatitud))

        # check if there is an event
        eventReport = EventForBusv2.objects.filter(
            timeStamp__gt=oldestAlertedTime, 
            busassignment=theAssignment, 
            event=theEvent).order_by('-timeStamp').first()

        if eventReport is not None:
            # updates to the event reported
            eventReport.timeStamp = aTimeStamp

            # update the counters
            if pConfirmDecline == 'decline':
                eventReport.eventDecline += 1
            else:
                eventReport.eventConfirm += 1
        else:
            # if an event was not found, create a new one
            eventReport = EventForBusv2.objects.create(
                phoneId=pPhoneId,
                busassignment=theAssignment,
                event=theEvent,
                timeStamp=aTimeStamp,
                timeCreation=aTimeStamp)

            # set the initial values for this fields
            if pConfirmDecline == 'decline':
                eventReport.eventDecline = 1
                eventReport.eventConfirm = 0

        eventReport.save()

        StadisticDataFromRegistrationBus.objects.create(
            timeStamp=aTimeStamp,
            confirmDecline=pConfirmDecline,
            reportOfEvent=eventReport,
            longitud=pLongitud,
            latitud=pLatitud,
            phoneId=pPhoneId,
            gpsLongitud=responseLongitud,
            gpsLatitud=responseLatitud,
            gpsTimeStamp=responseTimeStamp,
            distance=responseDistance)

        # Returns updated event list for a bus
        return EventsByBusV2().get(request, theBus.uuid)
