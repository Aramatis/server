from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.core.exceptions import ValidationError

from AndroidRequests.models import Event, Busv2, EventForBusv2, StadisticDataFromRegistrationBus, Busassignment, \
    TranSappUser
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
from AndroidRequests.encoder import TranSappJSONEncoder

from onlinegps.views import get_real_machine_info_with_distance

import AndroidRequests.scoreFunctions as score
import json


class RegisterEventBusV2(View):
    """This class handles requests that report events of a bus."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterEventBusV2, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ """
        phone_id = request.POST.get('phoneId', '')
        machine_id = request.POST.get('machineId', '')
        route = request.POST.get('service', '')

        event_id = request.POST.get('eventId', '')
        vote = request.POST.get('vote', '')
        latitude = float(request.POST.get('latitude', '500'))
        longitude = float(request.POST.get('longitude', '500'))

        user_id = request.POST.get('userId')
        session_token = request.POST.get('sessionToken')

        return self.get(request, phone_id, machine_id, route,
                        event_id, vote, latitude, longitude, user_id, session_token)

    def get(
            self,
            request,
            phone_id,
            machine_id,
            route,
            event_id,
            confirm_or_decline,
            latitude=500,
            longitude=500,
            user_id=None,
            session_token=None):
        # here we request all the info needed to proceed
        event_obj = Event.objects.get(id=event_id)
        timestamp = timezone.now()
        expire_time = timestamp + timezone.timedelta(minutes=event_obj.lifespam)

        # remove hyphen and convert to uppercase
        # pBusPlate = pBusPlate.replace('-', '').upper()
        try:
            bus_obj = Busv2.objects.get(uuid=machine_id)
            bus_assignment = Busassignment.objects.get(uuid=bus_obj, service=route)
        except (Busv2.DoesNotExist, Busassignment.DoesNotExist):
            return JsonResponse({}, safe=False, encoder=TranSappJSONEncoder)

        # get the GPS data from the url
        response_longitude, response_latitude, response_time_stamp, response_distance = \
            get_real_machine_info_with_distance(bus_obj.registrationPlate, float(longitude), float(latitude))

        # check if there is an event
        event_report = EventForBusv2.objects.filter(
            expireTime__gte=timestamp,
            timeCreation__lte=timestamp,
            busassignment=bus_assignment,
            broken=False,
            event=event_obj).order_by('-timeStamp').first()

        if event_report is not None:
            # updates to the event reported
            event_report.timeStamp = timestamp
            event_report.expireTime = expire_time

            # update the counters
            if confirm_or_decline == EventForBusv2.DECLINE:
                event_report.eventDecline += 1
            else:
                event_report.eventConfirm += 1
        else:
            # if an event was not found, create a new one
            event_report = EventForBusv2.objects.create(
                phoneId=phone_id,
                busassignment=bus_assignment,
                event=event_obj,
                timeStamp=timestamp,
                expireTime=expire_time,
                timeCreation=timestamp)

            # set the initial values for this fields
            if confirm_or_decline == EventForBusv2.DECLINE:
                event_report.eventDecline = 1
                event_report.eventConfirm = 0

        event_report.save()

        transapp_user = None
        try:
            transapp_user = TranSappUser.objects.get(userId=user_id, sessionToken=session_token)
        except (TranSappUser.DoesNotExist, ValidationError):
            pass

        StadisticDataFromRegistrationBus.objects.create(
            timeStamp=timestamp,
            confirmDecline=confirm_or_decline,
            reportOfEvent=event_report,
            longitude=longitude,
            latitude=latitude,
            phoneId=phone_id,
            gpsLongitude=response_longitude,
            gpsLatitude=response_latitude,
            gpsTimeStamp=response_time_stamp,
            distance=response_distance,
            tranSappUser=transapp_user)

        # update score
        json_score_response = score.calculate_event_score(request, event_id)
        # Returns updated event list for a bus
        json_event_response = json.loads(EventsByBusV2().get(request, machine_id).content)
        json_event_response["gamificationData"] = json_score_response

        return JsonResponse(json_event_response, encoder=TranSappJSONEncoder)
