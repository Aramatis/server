from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

import logging

# python utilities
import requests
import json
import re

# my stuff
# import DB's models
from AndroidRequests.models import DevicePositionInTime, BusStop, NearByBusesLog, Busv2, Busassignment, Service, ServicesByBusStop, Token
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
# constants
import AndroidRequests.constants as Constants


def userPosition(request, pUserId, pLat, pLon):
    '''This function stores the pose of an active user'''
    # the pose is stored
    currPose = DevicePositionInTime(
        longitud=pLon,
        latitud=pLat,
        timeStamp=timezone.now(),
        userId=pUserId)
    currPose.save()

    response = {'response': 'Pose registered.'}
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
        NearByBusesLog.objects.create(
            userId=pUserId,
            busStop=theBusStop,
            timeStamp=timeNow)
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
    userBuses = getUserBuses(theBusStop, pUserId)

    """
    DTPM BUSES
    """
    # DTPM source
    url = "http://54.94.231.101/dtpm/busStopInfo/"
    url = "{}{}/{}".format(url, settings.SECRET_KEY, pBusStop)
    response = requests.get(url=url)

    authBuses = []
    if(response.text != ""):
        data = json.loads(response.text)
        
        if 'id' in data:
            authBuses = getAuthorityBuses(data)

        if data['error'] is not None:
            answer['DTPMError'] = data['error']
        else:
            answer['DTPMError'] = ""

    """
    MERGE USER BUSES WITH DTPM BUSES
    """
    answer['servicios'] = mergeBuses(userBuses, authBuses)

    return JsonResponse(answer, safe=False)


def formatServiceName(serviceName):
    """ apply common format used by transantiago to show service name to user  """
    if not serviceName[-1:] == 'N':
        serviceName = "{}{}".format(serviceName[0], serviceName[1:].lower())
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
        if 0 <= distance and distance <= 100:
            return "Llegando"
        else:
            return "0 a {} min".format(menosd.group(1))

    entre = re.match("Entre (\d+) Y (\d+) min.", time)
    if entre is not None:
        return "{} a {} min".format(entre.group(1), entre.group(2))

    enmenosd = re.match("En menos de (\d+) min.", time)
    if enmenosd:
        if 0 <= distance and distance <= 100:
            return "Llegando"
        else:
            return "0 a {} min".format(enmenosd.group(1))

    masd = re.match("Mas de (\d+) min.", time)
    if masd is not None:
        return "+ de {} min".format(masd.group(1))

    return time


def getUserBuses(theBusStop, questioner):
    """ get active user buses """

    logger = logging.getLogger(__name__)

    servicesToBusStop = ServicesByBusStop.objects.filter(busStop=theBusStop)
    serviceNames = []
    serviceDirections = []
    for s in servicesToBusStop:
        serviceNames.append(s.service.service)
        serviceDirections.append(s.code.replace(s.service.service, ""))

    # active user buses that stop in the bus stop
    activeUserBuses = Token.objects.filter(
        busassignment__service__in=serviceNames,
        activetoken__isnull=False)
    # print "usuarios activos: " + str(len(activeUserBuses))

    userBuses = []
    uuids = []
    for user in activeUserBuses:
        serviceIndex = serviceNames.index(user.busassignment.service)
        uuid = user.busassignment.uuid.uuid
        # TODO: consider bus direction
        if user.direction == serviceDirections[
                serviceIndex] and (uuid not in uuids):
            uuids.append(uuid)
            bus = {}
            bus['servicio'] = user.busassignment.service
            bus['patente'] = user.busassignment.uuid.registrationPlate
            busEvents = EventsByBusV2().getEventsForBus([user.busassignment])
            bus['eventos'] = busEvents
            busData = user.busassignment.getLocation()
            bus['lat'] = busData['latitude']
            bus['lon'] = busData['longitude']
            bus['tienePasajeros'] = busData['passengers']
            try:
                bus['sentido'] = user.busassignment.getDirection(
                    theBusStop.code, 30)
            except Exception as e:
                logger.error(str(e))
                bus['sentido'] = "left"
            bus['color'] = Service.objects.get(
                service=bus['servicio']).color_id
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
            bus['busId'] = uuid
            bus['direction'] = user.direction
            bus['isTheSameUser'] = True if str(
                user.userId) == questioner else False
            # assume that bus is 30 meters from bus stop to predict direction
            if not bus['random']:
                userBuses.append(bus)

    return userBuses


def getAuthorityBuses(data):
    """ apply json format to authority info """

    logger = logging.getLogger(__name__)
    
    authBuses = []
    busStopCode = data['id']
    for service in data['servicios']:
        if service['valido'] != 1 or service['patente'] is None \
           or service['tiempo'] is None or service['distancia'] == 'None mts.':
            continue
        # clean the strings from spaces and unwanted format
        service['servicio'] = formatServiceName(service['servicio'].strip())
        service['patente'] = service[
            'patente'].replace("-", "").strip().upper()
        distance = int(service['distancia'].replace(' mts.', ''))
        service['distanciaMts'] = distance
        service['distanciaV2'] = formatDistance(distance)
        service['tiempoV2'] = formatTime(service['tiempo'], distance)

        # request the correct bus
        bus = Busv2.objects.get_or_create(
            registrationPlate=service['patente'])[0]
        busassignment = Busassignment.objects.get_or_create(
            service=service['servicio'], uuid=bus)[0]
        service['random'] = False

        try:
            busData = busassignment.getEstimatedLocation(busStopCode, distance)
        except Exception as e:
            logger.error(str(e))
            busData = {}
            busData['latitude'] = 500
            busData['longitude'] = 500
            busData['direction'] = 'I'
            service['random'] = True

        service['tienePasajeros'] = 0
        service['lat'] = busData['latitude']
        service['lon'] = busData['longitude']
        service['direction'] = busData['direction']
        service['color'] = Service.objects.get(
            service=service['servicio']).color_id

        try:
            service['sentido'] = busassignment.getDirection(
                busStopCode, distance)
        except Exception as e:
            logger.error(str(e))
            service['sentido'] = "left"

        getEventBus = EventsByBusV2()
        busEvents = getEventBus.getEventsForBus([busassignment])
        service['eventos'] = busEvents
        # add uuid parameter
        service['busId'] = bus.uuid

        authBuses.append(service)

    return authBuses


def mergeBuses(userBuses, authorityBuses):
    """ Join the list of user buses with authority buses """
    buses = []

    for userBus in userBuses:
        # print "user bus: " + str(userBus['patente'])
        if userBus['patente'] == Constants.DUMMY_LICENSE_PLATE and not userBus[
                'isTheSameUser']:
            # print "added dummy bus to list"
            buses.append(userBus)
        else:
            for authBus in authorityBuses:
                # print "compare {}=={} and {}=={}".format(authBus['servicio'],
                # userBus['servicio'], authBus['patente'], userBus['patente'])
                if authBus['servicio'] == userBus['servicio'] and \
                   authBus['patente'].upper() == userBus['patente'].upper():
                    userBus['tiempo'] = authBus['tiempo']
                    userBus['tiempoV2'] = authBus['tiempoV2']
                    userBus['distancia'] = authBus['distancia']
                    userBus['distanciaV2'] = authBus['distanciaV2']
                    userBus['distanciaMts'] = authBus['distanciaMts']
                    userBus['sentido'] = authBus['sentido']
                    if not userBus['isTheSameUser']:
                        buses.append(userBus)
                    authorityBuses.remove(authBus)
                    # p rint "son iguales"
                    # print str(userBus)
                else:
                    pass
                    # pass
                    # print "no son iguales"
                    # answer['servicios'].append(userBus)

    buses.extend(authorityBuses)

    return buses
