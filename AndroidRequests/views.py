from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

#python utilities
import requests
import json
from random import uniform

# my stuff
# import DB's models
from AndroidRequests.models import DevicePositionInTime, BusStop, NearByBusesLog, Bus, Service, ServicesByBusStop, Token
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.EventsByBus import EventsByBus
# constants
import AndroidRequests.constants as Constants

def userPosition(request, pUserId, pLat, pLon):
    '''This function stores the pose of an active user'''
    # the pose is stored
    currPose = DevicePositionInTime(longitud = pLon, latitud = pLat \
    ,timeStamp = timezone.now(), userId = pUserId)
    currPose.save()

    response = {'response':'Pose registered.'}
    return JsonResponse(response, safe=False)

def nearbyBuses(request, pUserId, pBusStop):
    """ return all information about bus stop: events and buses """

    timeNow = timezone.now()
    theBusStop = BusStop.objects.get(code=pBusStop)

    # Register user request
    NearByBusesLog.objects.create(userId = pUserId, busStop = theBusStop, timeStamp = timeNow)

    answer = {}
    """
    BUS STOP EVENTS
    """
    getEventsBusStop = EventsByBusStop()
    busStopEvent = getEventsBusStop.getEventsForBusStop(theBusStop, timeNow)
    answer["eventos"] = busStopEvent

    """
    USER BUSES
    """
    servicesToBusStop = ServicesByBusStop.objects.filter(busStop = theBusStop)
    serviceNames = []
    serviceDirections = []
    for s in servicesToBusStop:
        serviceNames.append(s.service.service)
        serviceDirections.append(s.code.replace(s.service.service, ""))

    # active user buses that stop in the bus stop
    activeUserBuses = Token.objects.filter(bus__service__in = serviceNames, \
            activetoken__isnull=False)

    activeUserBusesToBusStop = []
    for user in activeUserBuses:
        serviceIndex = serviceNames.index(user.bus.service)
        #TODO: consider bus direction
        if user.direction == serviceDirections[serviceIndex] or \
            user.direction is None:
            activeUserBusesToBusStop.append(user.bus)

    userBuses = []
    for userBus in activeUserBusesToBusStop:
        bus = {}
        bus['servicio'] = userBus.service
        bus['patente'] = userBus.registrationPlate
        busEvents = EventsByBus().getEventForBus(userBus)
        bus['eventos'] = busEvents
        busData = userBus.getLocation()
        bus['lat'] = busData['latitude']
        bus['lon'] = busData['longitude']
        bus['tienePasajeros'] = busData['passengers']
        bus['sentido'] = userBus.getDirection(pBusStop, 30)
        bus['color'] = Service.objects.get(service=bus['servicio']).color_id
        bus['random'] = busData['random']
        # extras
        bus['tiempo'] = 'transmitiendo'
        bus['distancia'] = '1 mts.'
        bus['valido'] = 1
        # assume that bus is 30 meters from bus stop to predict direction
        if not bus['random']:
            userBuses.append(bus)

    """
    DTPM BUSES
    """

    # DTPM source
    url = "http://54.94.231.101/dtpm/busStopInfo/"
    url = "{}{}/{}".format(url, settings.SECRET_KEY, pBusStop)
    response = requests.get(url=url)

    dtpmBuses = []
    if(response.text != ""):
        data = json.loads(response.text)
        data['error'] = None

        busStopCode = data['id']

        for service in data['servicios']:
            if service['valido']!=1 or service['patente'] is None \
               or service['tiempo'] is None or service['distancia']=='None mts.':
                continue
            # clean the strings from spaces and unwanted format
            service['servicio']  = service['servicio'].strip()
            service['patente']   = service['patente'].replace("-", "")
            service['patente']   = service['patente'].strip()
            service['servicio']  = formatServiceName(service['servicio'])
            distance = service['distancia'].replace(' mts.', '')

            # request the correct bus
            bus = Bus.objects.get_or_create(registrationPlate = service['patente'], \
                    service = service['servicio'])[0]
            busData = bus.getEstimatedLocation(busStopCode, distance)
            service['tienePasajeros'] = busData['passengers']
            service['lat'] = busData['latitud']
            service['lon'] = busData['longitud']
            #service['random'] = busData['random']
            #TODO: log unregistered services
            service['color'] = Service.objects.get(service=service['servicio']).color_id
            service['sentido'] = bus.getDirection(busStopCode, distance)
            service['random'] = False

            getEventBus = EventsByBus()
            busEvents = getEventBus.getEventForBus(bus)
            service['eventos'] = busEvents

            dtpmBuses.append(service)

        if data['error'] != None:
            answer['DTPMError'] = data['error']
        else:
            answer['DTPMError'] = ""

    """
    MERGE USER BUSES WITH DTPM BUSES
    """
    answer['servicios'] = []
    for userBus in userBuses:
        if userBus['patente'] == Constants.DUMMY_LICENSE_PLATE:
            answer['servicios'].append(userBus)
        else:
            for dtpmBus in dtpmBuses:
                if dtpmBus['servicio'] == userBus['servicio'] and \
                   dtpmBus['patente'] == userBus['patente']:
                    userBus['tiempo'] = dtpmBus['tiempo']
                    userBus['distancia'] = dtpmBus['distancia']
                    userBus['sentido'] = dtpmBus['sentido']
                    answer['servicios'].append(userBus)
                    dtpmBuses.remove(dtpmBus)
                    continue

    answer['servicios'].extend(dtpmBuses)

    return JsonResponse(answer, safe=False)

def formatServiceName(serviceName):
    """ apply common format used by transantiago to show service name to user  """
    if not serviceName[-1:] == 'N':
        serviceName = "{}{}".format(serviceName[0],serviceName[1:].lower())
    return serviceName
