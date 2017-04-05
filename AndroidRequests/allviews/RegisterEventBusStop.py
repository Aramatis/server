from django.views.generic import View
from django.utils import timezone
<<<<<<< HEAD
from django.conf import settings
=======
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
>>>>>>> feature/usersAndScore

import json
# my stuff
# import DB's models
from AndroidRequests.models import Event, BusStop, EventForBusStop, StadisticDataFromRegistrationBusStop

from EventsByBusStop import EventsByBusStop

import AndroidRequests.scoreFunctions as score

class RegisterEventBusStop(View):
    '''This class handles the requests that report events of a bus stop'''

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterEventBusStop, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ """
        phoneId = request.POST.get('phoneId', '')
        stopCode = request.POST.get('stopCode', '')

        eventCode = request.POST.get('eventId', '')
        vote = request.POST.get('vote', '')
        # user position
        userLatitude = float(request.POST.get('latitude', '500'))
        userLongitude = float(request.POST.get('longitude', '500'))
        
        userId = request.POST.get('userId', '')
        sessionToken = request.POST.get('sessionToken', '')

        service = request.POST.get('service', '')

        return self.get(request, phoneId, stopCode,  
                eventCode, vote, userLatitude, userLongitude, service)

    def get(
            self,
            request,
            pPhoneId,
            stopCode,
            pEventID,
            pConfirmDecline,
            pLatitud=500,
            pLongitud=500,
            pService=''):

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
        else:
            eventReport = EventForBusStop.objects.create(
                busStop=theBusStop,
                event=theEvent,
                timeStamp=aTimeStamp,
                timeCreation=aTimeStamp,
                userId=pPhoneId,
                aditionalInfo=pService)

            if pConfirmDecline == 'decline':
                eventReport.eventDecline = 1
                eventReport.eventConfirm = 0

        eventReport.save()

        StadisticDataFromRegistrationBusStop.objects.create(
            timeStamp=aTimeStamp,
            confirmDecline=pConfirmDecline,
            reportOfEvent=eventReport,
            longitud=pLongitud,
            latitud=pLatitud,
            userId=pPhoneId)

        # update score
        jsonScoreResponse = score.calculateEventScore(request, pEventID)
        # Returns updated event list for a bus stop
        jsonEventResponse = json.loads(EventsByBusStop().get(request, pBusStopCode).content)
        jsonEventResponse["gamificationData"] = jsonScoreResponse

        return JsonResponse(jsonEventResponse)

    def getLastEvent(self, querySet):
        toReturn = querySet[0]

        for val in range(len(querySet) - 1):
            if toReturn.timeStamp < val.timeStamp:
                toReturn = val

        return toReturn
