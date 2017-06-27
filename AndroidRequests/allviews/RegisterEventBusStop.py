import json

from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import AndroidRequests.scoreFunctions as score
# my stuff
# import DB's models
from AndroidRequests.models import Event, EventForBusStop, StadisticDataFromRegistrationBusStop, TranSappUser
from EventsByBusStop import EventsByBusStop


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
        
        userId = request.POST.get('userId')
        sessionToken = request.POST.get('sessionToken')

        service = request.POST.get('service', '')

        return self.get(request, phoneId, stopCode,  
                eventCode, vote, userLatitude, userLongitude, service, userId, sessionToken)

    def get(
            self,
            request,
            pPhoneId,
            stopCode,
            pEventID,
            pConfirmDecline,
            pLatitude=500,
            pLongitude=500,
            pService='',
            userId=None,
            sessionToken=None):

        event = Event.objects.get(id=pEventID)
        timeStamp = timezone.now()
        expireTime = timeStamp + timezone.timedelta(minutes=event.lifespam)

        eventReport = EventForBusStop.objects.filter(
            expireTime__gte=timeStamp, 
            timeCreation__lte=timeStamp, 
            stopCode=stopCode, 
            broken = False,
            event=event).order_by('-timeStamp').first()

        if eventReport is not None:
            # updates to the event reported
            eventReport.timeStamp = timeStamp
            eventReport.expireTime = expireTime
            if pConfirmDecline == 'decline':
                eventReport.eventDecline += 1
            else:
                eventReport.eventConfirm += 1
        else:
            eventReport = EventForBusStop.objects.create(
                stopCode=stopCode,
                event=event,
                timeStamp=timeStamp,
                expireTime=expireTime,
                timeCreation=timeStamp,
                phoneId=pPhoneId,
                aditionalInfo=pService)

            if pConfirmDecline == 'decline':
                eventReport.eventDecline = 1
                eventReport.eventConfirm = 0

        eventReport.save()

        tranSappUser = None
        try:
            tranSappUser = TranSappUser.objects.get(userId=userId, sessionToken=sessionToken)
        except Exception:
            pass

        StadisticDataFromRegistrationBusStop.objects.create(
            timeStamp=timeStamp,
            confirmDecline=pConfirmDecline,
            reportOfEvent=eventReport,
            longitude=pLongitude,
            latitude=pLatitude,
            phoneId=pPhoneId,
            tranSappUser=tranSappUser)

        # update score
        jsonScoreResponse = score.calculateEventScore(request, pEventID)
        # Returns updated event list for a bus stop
        jsonEventResponse = json.loads(EventsByBusStop().get(request, stopCode).content)
        jsonEventResponse["gamificationData"] = jsonScoreResponse

        return JsonResponse(jsonEventResponse)
