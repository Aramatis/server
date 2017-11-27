from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from AndroidRequests.models import Event, Busv2, Busassignment, EventForBusv2, StadisticDataFromRegistrationBus
from EventsByBusV2 import EventsByBusV2
from AndroidRequests.encoder import TranSappJSONEncoder

from onlinegps.views import get_real_machine_info_with_distance

import AndroidRequests.constants as constants


class RegisterEventBus(View):
    """This class handles requests that report events of a bus."""

    def get(
            self,
            request,
            phone_id,
            route,
            license_plate,
            event_id,
            confirm_or_decline,
            latitude=500,
            longitude=500):
        # here we request all the info needed to proceed
        event = Event.objects.get(id=event_id)
        timestamp = timezone.now()
        expire_time = timestamp + timezone.timedelta(minutes=event.lifespam)

        # remove hyphen and convert to uppercase
        license_plate = license_plate.replace('-', '').upper()

        if license_plate == constants.DUMMY_LICENSE_PLATE:
            response = {}
            events = []
            dictionary = {}

            response['registrationPlate'] = license_plate
            response['service'] = route

            dictionary['eventConfirm'] = 1
            dictionary['eventDecline'] = 0
            creation = timezone.localtime(timezone.now())
            stamp = timezone.localtime(timezone.now())
            dictionary['timeCreation'] = creation.strftime("%d-%m-%Y %H:%M:%S")
            dictionary['timeStamp'] = stamp.strftime("%d-%m-%Y %H:%M:%S")
            dictionary.update(event.getDictionary())

            events.append(dictionary)
            # events[0].
            response['events'] = events
            return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
            # TODO
            # Problem: there is no way to identify THE dummy bus without the uuid.
            # Return the same event.
        else:
            bus = Busv2.objects.get_or_create(
                registrationPlate=license_plate)[0]
            bus_assignment = Busassignment.objects.get(
                service=route, uuid=bus)

        # get the GPS data from the url
        response_longitude, response_latitude, response_timestamp, response_distance = \
            get_real_machine_info_with_distance(bus.registrationPlate, float(longitude), float(latitude))

        # check if there is an event
        event_report = EventForBusv2.objects.filter(
            expireTime__gte=timestamp,
            timeCreation__lte=timestamp,
            busassignment=bus_assignment,
            event=event).order_by('-timeStamp').first()

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
                event=event,
                timeStamp=timestamp,
                expireTime=expire_time,
                timeCreation=timestamp)

            # set the initial values for this fields
            if confirm_or_decline == EventForBusv2.DECLINE:
                event_report.eventDecline = 1
                event_report.eventConfirm = 0

        event_report.save()

        StadisticDataFromRegistrationBus.objects.create(
            timeStamp=timestamp,
            confirmDecline=confirm_or_decline,
            reportOfEvent=event_report,
            longitude=longitude,
            latitude=latitude,
            phoneId=phone_id,
            gpsLongitude=response_longitude,
            gpsLatitude=response_latitude,
            gpsTimeStamp=response_timestamp,
            distance=response_distance)

        # Returns updated event list for a bus
        return EventsByBusV2().get(request, bus.uuid)
