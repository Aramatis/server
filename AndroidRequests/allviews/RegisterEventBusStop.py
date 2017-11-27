from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.core.exceptions import ValidationError

from AndroidRequests.encoder import TranSappJSONEncoder
from AndroidRequests.models import Event, EventForBusStop, StadisticDataFromRegistrationBusStop, TranSappUser
from EventsByBusStop import EventsByBusStop

import AndroidRequests.scoreFunctions as score
import json


class RegisterEventBusStop(View):
    """This class handles the requests that report events of a bus stop"""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterEventBusStop, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ """
        phone_id = request.POST.get('phoneId', '')
        stop_code = request.POST.get('stopCode', '')

        event_id = request.POST.get('eventId', '')
        vote = request.POST.get('vote', '')
        # user position
        user_latitude = float(request.POST.get('latitude', '500'))
        user_longitude = float(request.POST.get('longitude', '500'))

        user_id = request.POST.get('userId')
        session_token = request.POST.get('sessionToken')

        route = request.POST.get('service', '')

        return self.get(request, phone_id, stop_code,
                        event_id, vote, user_latitude, user_longitude, route, user_id, session_token)

    def get(
            self,
            request,
            phone_id,
            stop_code,
            event_id,
            confirm_or_decline,
            latitude=500,
            longitude=500,
            route='',
            user_id=None,
            session_token=None):

        event = Event.objects.get(id=event_id)
        timestamp = timezone.now()
        expire_time = timestamp + timezone.timedelta(minutes=event.lifespam)

        event_report = EventForBusStop.objects.filter(
            expireTime__gte=timestamp,
            timeCreation__lte=timestamp,
            stopCode=stop_code,
            broken=False,
            event=event).order_by('-timeStamp').first()

        if event_report is not None:
            # updates to the event reported
            event_report.timeStamp = timestamp
            event_report.expireTime = expire_time
            if confirm_or_decline == EventForBusStop.DECLINE:
                event_report.eventDecline += 1
            else:
                event_report.eventConfirm += 1
        else:
            event_report = EventForBusStop.objects.create(
                stopCode=stop_code,
                event=event,
                timeStamp=timestamp,
                expireTime=expire_time,
                timeCreation=timestamp,
                phoneId=phone_id,
                aditionalInfo=route)

            if confirm_or_decline == EventForBusStop.DECLINE:
                event_report.eventDecline = 1
                event_report.eventConfirm = 0

        event_report.save()

        transapp_user = None
        try:
            transapp_user = TranSappUser.objects.get(userId=user_id, sessionToken=session_token)
        except (TranSappUser.DoesNotExist, ValidationError):
            pass

        StadisticDataFromRegistrationBusStop.objects.create(
            timeStamp=timestamp,
            confirmDecline=confirm_or_decline,
            reportOfEvent=event_report,
            longitude=longitude,
            latitude=latitude,
            phoneId=phone_id,
            tranSappUser=transapp_user)

        # update score
        json_score_response = score.calculate_event_score(request, event_id)
        # Returns updated event list for a bus stop
        json_event_response = json.loads(EventsByBusStop().get(request, stop_code).content)
        json_event_response["gamificationData"] = json_score_response

        return JsonResponse(json_event_response, encoder=TranSappJSONEncoder)
