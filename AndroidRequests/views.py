from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

import logging

#python utilities
import requests
import json
from random import uniform
import re

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

    logger = logging.getLogger(__name__)

    timeNow = timezone.now()
    theBusStop = BusStop.objects.get(code=pBusStop)

    """
    This is temporal, it has to be deleted in the future
    """
    if pUserId != 'null':
        # Register user request
        NearByBusesLog.objects.create(userId = pUserId, busStop = theBusStop, timeStamp = timeNow)
    else:
        logger.error('nearbybuses: null user')

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
    #print "usuarios activos: " + str(len(activeUserBuses))
    
    userBuses = []
    for user in activeUserBuses:
        serviceIndex = serviceNames.index(user.bus.service)
        #TODO: consider bus direction
        if user.direction == serviceDirections[serviceIndex] or \
            user.direction is None:
            bus = {}
            bus['servicio'] = user.bus.service
            bus['patente'] = user.bus.registrationPlate
            busEvents = EventsByBus().getEventForBus(user.bus)
            bus['eventos'] = busEvents
            busData = user.bus.getLocation()
            bus['lat'] = busData['latitude']
            bus['lon'] = busData['longitude']
            bus['tienePasajeros'] = busData['passengers']
            try:
                bus['sentido'] = user.bus.getDirection(pBusStop, 30)
            except Exception as e:
                logger.error(str(e))
                bus['sentido'] = "left"
            bus['color'] = Service.objects.get(service=bus['servicio']).color_id
            bus['random'] = busData['random']
            bus['valido'] = 1
            # extras
            # old version, 1.2.17 and previous
            bus['tiempo'] = 'Viajando'
            bus['distancia'] = '1 mts.'
            # new version, 1.4.23 and upper
            bus['tiempoV2'] = 'Viajando'
            bus['distanciaV2'] = 'Usuario'
            bus['distanciaMts'] = 1
            # add new param 'uuid'
            bus['busId'] = user.bus.uuid
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
            service['servicio']  = formatServiceName(service['servicio'].strip())
            service['patente']   = service['patente'].replace("-", "").strip().upper()
            distance = int(service['distancia'].replace(' mts.', ''))
            service['distanciaMts'] = distance
            service['distanciaV2'] = formatDistance(distance)
            service['tiempoV2'] = formatTime(service['tiempo'], distance)

            # request the correct bus
            bus = Bus.objects.get_or_create(registrationPlate = service['patente'], \
                    service = service['servicio'])[0]
            service['random'] = False
            try:
                busData = bus.getEstimatedLocation(busStopCode, distance)
            except Exception as e:
                logger.error(str(e))
                busData = {}
                busData['latitude'] = 500
                busData['longitude'] = 500
                service['random'] = True
            service['tienePasajeros'] = 0
            service['lat'] = busData['latitude']
            service['lon'] = busData['longitude']
            service['color'] = Service.objects.get(service=service['servicio']).color_id
            try:
                service['sentido'] = bus.getDirection(busStopCode, distance)
            except Exception as e:
                logger.error(str(e))
                service['sentido'] = "left"

            getEventBus = EventsByBus()
            busEvents = getEventBus.getEventForBus(bus)
            service['eventos'] = busEvents
            #add uuid parameter
            service['busId'] = bus.uuid

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
        #print "reviso un bus " + str(userBus['patente'])
        if userBus['patente'] == Constants.DUMMY_LICENSE_PLATE:
            #print "agrego dummy bus a la lista"
            answer['servicios'].append(userBus)
        else:
            for dtpmBus in dtpmBuses:
                #print "comparo {}=={} Y {}=={}".format(dtpmBus['servicio'], userBus['servicio'], dtpmBus['patente'], userBus['patente'])
                if dtpmBus['servicio'] == userBus['servicio'] and \
                   dtpmBus['patente'].upper() == userBus['patente'].upper():
                    userBus['tiempo'] = dtpmBus['tiempo']
                    userBus['tiempoV2'] = dtpmBus['tiempo']
                    userBus['distancia'] = dtpmBus['distancia']
                    userBus['distanciaV2'] = dtpmBus['distanciaV2']
                    userBus['distanciaMts'] = dtpmBus['distanciaMts']
                    userBus['sentido'] = dtpmBus['sentido']
                    answer['servicios'].append(userBus)
                    dtpmBuses.remove(dtpmBus)
                    #print "son iguales"
                    #print str(userBus)
                else:
                    pass
                    #pass
                    #print "no son iguales"
                    #answer['servicios'].append(userBus)

    answer['servicios'].extend(dtpmBuses)

    return JsonResponse(answer, safe=False)

def formatServiceName(serviceName):
    """ apply common format used by transantiago to show service name to user  """
    if not serviceName[-1:] == 'N':
        serviceName = "{}{}".format(serviceName[0],serviceName[1:].lower())
    return serviceName

def formatDistance(distance):
    """ format distance to show final user """
    distance = int(distance)
    if distance >= 1000:
        distance = round(float(distance) / 1000, 2)
        if distance.is_integer():
            return "{}Km".format(int(distance))
        else:
            return "{}Km".format(distance)
    else:
        return "{}m".format(distance)

def formatTime(time, distance):
    """ return a message related the time when a bus arrives to bus stop """
    menosd = re.match("Menos de (\d+) min.", time)
    if menosd:
        if 0 <= distance and distance <=100 :
            return "Llegando"
        else:
            return "0 a {} min".format(menosd.group(1))

    entre = re.match("Entre (\d+) Y (\d+) min.", time)
    if entre is not None:
        return "{} a {} min".format(entre.group(1), entre.group(2))

    enmenosd =re.match("En menos de (\d+) min.", time)
    if enmenosd:
        if 0 <= distance and distance <=100 :
            return "Llegando"
        else:
            return "0 a {} min".format(enmenosd.group(1))

    masd = re.match("Mas de (\d+) min.", time)
    if masd is not None:
        return "+ de {} min".format(masd.group(1))

    return time

