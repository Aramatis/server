from django.views.generic import View
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
# my stuff
# import DB's models
from AndroidRequests.models import Event, Busv2, EventForBusv2, StadisticDataFromRegistrationBus, Busassignment

from EventsByBusV2 import EventsByBusV2
import AndroidRequests.gpsFunctions as Gps
import AndroidRequests.scoreFunctions as score


class RegisterEventBusV2(View):
    '''This class handles requests that report events of a bus.'''

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterEventBusV2, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ """
        phoneId = request.POST.get('phoneId', '')
        machineId = request.POST.get('machineId', '')
        service = request.POST.get('service', '')

        eventCode = request.POST.get('eventId', '')
        vote = request.POST.get('vote', '')
        latitude = float(request.POST.get('latitude', '500'))
        longitude = float(request.POST.get('longitude', '500'))
        
        userId = request.POST.get('userId', '')
        sessionToken = request.POST.get('sessionToken', '')

        return self.get(request, phoneId, machineId, service, 
                eventCode, vote, latitude, longitude)

    def get(
            self,
            request,
            pPhoneId,
            pMachineId,
            pBusService,
            pEventID,
            pConfirmDecline,
            pLatitud=500,
            pLongitud=500):
        # here we request all the info needed to proceed
        aTimeStamp = timezone.now()
        theEvent = Event.objects.get(id=pEventID)

        # remove hyphen and convert to uppercase
        # pBusPlate = pBusPlate.replace('-', '').upper()
        theBus = {}
        theAsignment = {}
        try:
            theBus = Busv2.objects.get(uuid=pMachineId)
            theAsignment = Busassignment.objects.get(
                uuid=theBus, service=pBusService)
        except:
            return JsonResponse({}, safe=False)
        # theBus = Bus.objects.get(service=pBusService, uuid=pMachineId)
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
        if EventForBusv2.objects.filter(
                timeStamp__gt=oldestAlertedTime,
                busassignment=theAsignment,
                event=theEvent).exists():
            # get the event
            eventsReport = EventForBusv2.objects.filter(
                timeStamp__gt=oldestAlertedTime, busassignment=theAsignment, event=theEvent)
            eventReport = self.getLastEvent(eventsReport)

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
                userId=pPhoneId,
                busassignment=theAsignment,
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
            userId=pPhoneId,
            gpsLongitud=responseLongitud,
            gpsLatitud=responseLatitud,
            gpsTimeStamp=responseTimeStamp,
            distance=responseDistance)

        # update score
        jsonScoreResponse = score.calculateEventScore(request, pEventID)
        # Returns updated event list for a bus
        jsonEventResponse = json.loads(EventsByBusV2().get(request, pMachineId).content)
        jsonEventResponse["gamificationData"] = jsonScoreResponse

        return JsonResponse(jsonEventResponse)

    def getLastEvent(self, querySet):
        """if the query has two responses, return the latest one"""
        toReturn = querySet[0]

        for val in range(len(querySet) - 1):
            if toReturn.timeStamp < val.timeStamp:
                toReturn = val

        return toReturn
