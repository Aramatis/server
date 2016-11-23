from django.views.generic import View
from django.utils import timezone
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
import AndroidRequests.constants as Constants

# my stuff
# import DB's models
from AndroidRequests.models import Event, Busv2, EventForBusv2, StadisticDataFromRegistrationBus, Busassignment

from EventsByBusV2 import EventsByBusV2
import urllib2
import json

class RegisterEventBusV2(View):
    '''This class handles requests that report events of a bus.'''

    def get(self, request, pUserId, pUuid, pBusService, pEventID, pConfirmDecline, pLatitud=500, pLongitud=500):
        # here we request all the info needed to proceed
        aTimeStamp = timezone.now()
        theEvent = Event.objects.get(id=pEventID)

        # remove hyphen and convert to uppercase
        # pBusPlate = pBusPlate.replace('-', '').upper()
        theBus = {}
        theAsignment = {}
        try:
            theBus = Busv2.objects.get(uuid=pUuid)
            theAsignment = Busassignment.objects.get(uuid = theBus, service = pBusService)
        except:
            return JsonResponse({}, safe=False)
        #theBus = Bus.objects.get(service=pBusService, uuid=pUuid)
        # estimate the oldest time where the reported event can be usefull
        # if there is no event here a new one is created
        oldestAlertedTime = aTimeStamp - timezone.timedelta(minutes=theEvent.lifespam)

        #get the GPS data from the url
        parameters = {}
        parameters['licencePlate'] = theBus.registrationPlate
        parameters['time'] = aTimeStamp.strftime("%Y-%m-%d %H:%M:%S").replace(" ", "%20")
        url = "http://200.9.100.91:8080/gpsonline/transappBusPosition/getEstimatedPosition"
        full_url = url + '?licencePlate=' + parameters['licencePlate'] + '&time=' + parameters['time']
        data = urllib2.urlopen(full_url)

        responseLongitud = None 
        responseLatitud = None
        responseTimeStamp = None
        
        try:
            response = json.load(data)
            if response['error'] == False and response['machine']['licencePlate'] == parameters['licencePlate']:
                responseLongitud = response['nearestGpsPoint']['longitude']
                responseLatitud = response['nearestGpsPoint']['latitude']
                responseTimeStamp = response['nearestGpsPoint']['time']                
                responseTimeStamp = parse_datetime(responseTimeStamp + Constants.TIMEZONE)
        except:
            pass
                
        # check if there is an event
        if EventForBusv2.objects.filter(timeStamp__gt = oldestAlertedTime, \
            busassignment=theAsignment, event=theEvent).exists():
            # get the event
            eventsReport = EventForBusv2.objects.filter(timeStamp__gt = oldestAlertedTime,\
                busassignment=theAsignment, event=theEvent)
            eventReport = self.getLastEvent(eventsReport)

            # updates to the event reported
            eventReport.timeStamp = aTimeStamp

            # update the counters
            if pConfirmDecline == 'decline':
                eventReport.eventDecline += 1
            else:
                eventReport.eventConfirm += 1

            eventReport.save()

            StadisticDataFromRegistrationBus.objects.create(timeStamp=aTimeStamp, confirmDecline=pConfirmDecline,\
             reportOfEvent=eventReport, longitud=pLongitud, latitud=pLatitud, userId=pUserId, gpsLongitud=responseLongitud ,\
             gpsLatitud=responseLatitud ,gpsTimeStamp=responseTimeStamp)
        else:
            # if an event was not found, create a new one
            aEventReport = EventForBusv2.objects.create(userId=pUserId, busassignment=theAsignment, event=theEvent, timeStamp=aTimeStamp,\
                                timeCreation=aTimeStamp)

            # set the initial values for this fields
            if pConfirmDecline == 'decline':
                aEventReport.eventDecline = 1
                aEventReport.eventConfirm = 0

            aEventReport.save()

            StadisticDataFromRegistrationBus.objects.create(timeStamp=aTimeStamp, confirmDecline=pConfirmDecline, \
                reportOfEvent=aEventReport, longitud=pLongitud, latitud=pLatitud, userId=pUserId, gpsLongitud=responseLongitud ,\
                gpsLatitud=responseLatitud ,gpsTimeStamp=responseTimeStamp)

        # Returns updated event list for a bus
        eventsByBus = EventsByBusV2()

        return eventsByBus.get(request, pUuid) 
        
    def getLastEvent(self, querySet):
        """if the query has two responses, return the latest one"""
        toReturn = querySet[0]

        for val in range(len(querySet)-1):
            if toReturn.timeStamp < val.timeStamp:
                toReturn = val

        return toReturn
