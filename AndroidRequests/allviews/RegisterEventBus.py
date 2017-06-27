from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

import AndroidRequests.constants as Constants
import AndroidRequests.gpsFunctions as Gps
# my stuff
# import DB's models
from AndroidRequests.models import Event, Busv2, Busassignment, EventForBusv2, StadisticDataFromRegistrationBus
from EventsByBusV2 import EventsByBusV2


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
            pLatitude=500,
            pLongitude=500):
        # here we request all the info needed to proceed
        event = Event.objects.get(id=pEventID)
        timeStamp = timezone.now()
        expireTime = timeStamp + timezone.timedelta(minutes=event.lifespam)

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
            eventDictionary = event.getDictionary()
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

        # get the GPS data from the url
        responseLongitude = None
        responseLatitude = None
        responseTimeStamp = None
        responseDistance = None

        responseLongitude, responseLatitude, responseTimeStamp, responseDistance = Gps.getGPSData(
            theBus.registrationPlate, timeStamp, float(pLongitude), float(pLatitude))

        # check if there is an event
        eventReport = EventForBusv2.objects.filter(
            expireTime__gte=timeStamp, 
            timeCreation__lte=timeStamp, 
            busassignment=theAssignment, 
            event=event).order_by('-timeStamp').first()

        if eventReport is not None:
            # updates to the event reported
            eventReport.timeStamp = timeStamp
            eventReport.expireTime = expireTime

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
                event=event,
                timeStamp=timeStamp,
                expireTime=expireTime,
                timeCreation=timeStamp)

            # set the initial values for this fields
            if pConfirmDecline == 'decline':
                eventReport.eventDecline = 1
                eventReport.eventConfirm = 0

        eventReport.save()

        StadisticDataFromRegistrationBus.objects.create(
            timeStamp=timeStamp,
            confirmDecline=pConfirmDecline,
            reportOfEvent=eventReport,
            longitude=pLongitude,
            latitude=pLatitude,
            phoneId=pPhoneId,
            gpsLongitude=responseLongitude,
            gpsLatitude=responseLatitude,
            gpsTimeStamp=responseTimeStamp,
            distance=responseDistance)

        # Returns updated event list for a bus
        return EventsByBusV2().get(request, theBus.uuid)
