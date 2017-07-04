import json
import logging
import re

# python utilities
import requests
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone

from collections import defaultdict

# constants
import AndroidRequests.constants as Constants
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
# my stuff
# import DB's models
from AndroidRequests.models import DevicePositionInTime, BusStop, NearByBusesLog, Busv2, Busassignment, Service, \
    ServicesByBusStop, Token


def userPosition(request, pPhoneId, pLat, pLon):
    '''This function stores the pose of an active user'''
    # the pose is stored
    currPose = DevicePositionInTime(
        longitude=pLon,
        latitude=pLat,
        timeStamp=timezone.now(),
        phoneId=pPhoneId)
    currPose.save()

    response = {'response': 'Pose registered.'}
    return JsonResponse(response, safe=False)


def nearbyBuses(request, pPhoneId, pBusStop):
    """ return all information about bus stop: events and buses """

    logger = logging.getLogger(__name__)

    timeNow = timezone.now()
    stopObj = BusStop.objects.get(code=pBusStop, gtfs__version=settings.GTFS_VERSION)

    """
    This is temporal, it has to be deleted in the future
    """
    if pPhoneId != 'null':
        # Register user request
        NearByBusesLog.objects.create(
            phoneId=pPhoneId,
            busStop=stopObj,
            timeStamp=timeNow)
    else:
        logger.error('nearbybuses: null user')

    answer = {}
    """
    BUS STOP EVENTS
    """
    busStopEvent = EventsByBusStop().getEventsForStop(pBusStop, timeNow)
    answer["eventos"] = busStopEvent

    """
    USER BUSES
    """
    userBuses = getUserBuses(stopObj, pPhoneId)

    """
    DTPM BUSES
    """
    # DTPM source
    url = "http://54.94.231.101/dtpm/busStopInfo/"
    url = "{}{}/{}".format(url, settings.SECRET_KEY, pBusStop)
    response = requests.get(url=url)

    authBuses = []
    if response.text != "":
        data = json.loads(response.text)

        if 'id' in data:
            authBuses = getAuthorityBuses(stopObj, data)

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
        if 0 <= distance <= 100:
            return "Llegando"
        else:
            return "0 a {} min".format(menosd.group(1))

    entre = re.match("Entre (\d+) Y (\d+) min.", time)
    if entre is not None:
        return "{} a {} min".format(entre.group(1), entre.group(2))

    enmenosd = re.match("En menos de (\d+) min.", time)
    if enmenosd:
        if 0 <= distance <= 100:
            return "Llegando"
        else:
            return "0 a {} min".format(enmenosd.group(1))

    masd = re.match("Mas de (\d+) min.", time)
    if masd is not None:
        return "+ de {} min".format(masd.group(1))

    return time


def getUserBuses(stopObj, questioner):
    """ get active user buses """

    logger = logging.getLogger(__name__)
    servicesToBusStop = ServicesByBusStop.objects.select_related('service').filter(busStop=stopObj,
                                                                                   gtfs__version=settings.GTFS_VERSION)
    serviceNames = []
    serviceDirections = []
    for s in servicesToBusStop:
        serviceNames.append(s.service.service)
        serviceDirections.append(s.code.replace(s.service.service, ""))

    # active user buses that stop in the bus stop
    activeUserBuses = Token.objects.select_related('tranSappUser', 'busassignment__uuid').filter(
        busassignment__service__in=serviceNames,
        activetoken__isnull=False)

    # retrieve events for all user buses
    busassignments = []
    for tokenObj in activeUserBuses:
        busassignments.append(tokenObj.busassignment)
    eventsByMachineId = EventsByBusV2().getEventsForBuses(busassignments, timezone.now())

    globalScores = []
    # used to choose which bus avatar shows. Criteria: user with highest global score
    userBuses = []
    uuids = []
    # bus identifiers
    for tokenObj in activeUserBuses:
        serviceIndex = serviceNames.index(tokenObj.busassignment.service)
        machineId = tokenObj.busassignment.uuid.uuid

        if machineId in uuids:
            position = uuids.index(machineId)
            bus = userBuses[position]
            if str(tokenObj.phoneId) == questioner:
                bus['isSameUser'] = True
            # update avatar id
            if tokenObj.tranSappUser is not None:
                globalScore = tokenObj.tranSappUser.globalScore
                if globalScores[position] < globalScore:
                    globalScores[position] = globalScore
                    bus['avatarId'] = tokenObj.tranSappUser.busAvatarId

            userBuses[position] = bus

        elif tokenObj.direction == serviceDirections[serviceIndex]:
            uuids.append(machineId)
            globalScores.append(0)

            bus = {'servicio': tokenObj.busassignment.service, 'patente': tokenObj.busassignment.uuid.registrationPlate,
                   'direction': tokenObj.direction,
                   'isSameUser': True if str(tokenObj.phoneId) == questioner else False}
            if tokenObj.tranSappUser is not None:
                position = len(globalScores) - 1
                globalScores[position] = tokenObj.tranSappUser.globalScore
                bus['avatarId'] = tokenObj.tranSappUser.busAvatarId
            else:
                bus['avatarId'] = 1
                # default bus avatar id

            busData = tokenObj.busassignment.getLocation()
            bus['random'] = busData['random']
            bus['lat'] = busData['latitude']
            bus['lon'] = busData['longitude']
            bus['tienePasajeros'] = busData['passengers']

            bus['eventos'] = eventsByMachineId[machineId] if machineId in eventsByMachineId.keys() else []

            try:
                # assume that bus is 30 meters from bus stop to predict direction
                bus['sentido'] = tokenObj.busassignment.getDirection(
                    stopObj, 30)
            except Exception as e:
                logger.error(str(e))
                bus['sentido'] = "left"

            bus['color'] = Service.objects.get(service=bus['servicio'],
                                               gtfs__version=settings.GTFS_VERSION).color_id
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
            bus['busId'] = machineId

            if not bus['random']:
                userBuses.append(bus)

    return userBuses


def getAuthorityBuses(stopObj, data):
    """ apply json format to authority info """

    logger = logging.getLogger(__name__)

    authBuses = []
    stopCode = data['id']

    """
    Generate busObjDict and busDict dicts to make just two queries to get all buses info
    """
    # TODO: 'replace("-", "").strip().upper()' has moved to webService app, so will have to disappear in the future
    routeList = filter(lambda route: route['patente'] is not None, data['servicios'])
    licensePlateList = map(lambda route: route['patente'].replace("-", "").strip().upper(), routeList)

    busObjList = Busv2.objects.prefetch_related('busassignment_set').filter(registrationPlate__in=licensePlateList)
    busObjDict = defaultdict(None)
    for busObj in busObjList:
        busObjDict[busObj.registrationPlate] = busObj

    busList = Busv2.objects.filter(registrationPlate__in=licensePlateList).values_list('registrationPlate',
                                                                                       'uuid',
                                                                                       'busassignment__service')
    busDict = defaultdict(lambda : {'busassignments': [], 'uuid': None})
    for licensePlate, uuid, route in busList:
        busDict[licensePlate]['busassignments'].append(route)
        busDict[licensePlate]['uuid'] = uuid

    """
    Generate eventBusObjDict dict to make one query to get all event buses info
    """
    busassignments = []
    for busObj in busObjList:
        busassignments += busObj.busassignment_set.all()
    eventsByMachineId = EventsByBusV2().getEventsForBuses(busassignments, timezone.now())

    for service in data['servicios']:
        if service['valido'] != 1 or service['patente'] is None \
                or service['tiempo'] is None or service['distancia'] == 'None mts.':
            continue
        # clean the strings from spaces and unwanted format
        service['servicio'] = formatServiceName(service['servicio'].strip())
        # TODO: this has moved to webService app, so will have to disappear in the future
        service['patente'] = service['patente'].replace("-", "").strip().upper()
        distance = int(service['distancia'].replace(' mts.', ''))
        service['distanciaMts'] = distance
        service['distanciaV2'] = formatDistance(distance)
        service['tiempoV2'] = formatTime(service['tiempo'], distance)

        licensePlate = service['patente']
        route = service['servicio']
        # request the correct bus
        if licensePlate not in busDict.keys():
            bus = Busv2.objects.create(registrationPlate=licensePlate)
            service['busId'] = bus.uuid
            busassignment = Busassignment.objects.create(service=route, uuid=bus)
        else:
            service['busId'] = busDict[service['patente']]['uuid']
            if route not in busDict[licensePlate]['busassignments']:
                busassignment = Busassignment.objects.create(service=route, uuid=busObjDict[licensePlate])
            else:
                # this uses prefetch related made in busObjList
                busassignment = [b for b in busObjDict[licensePlate].busassignment_set.all() if b.service == route][0]

        service['eventos'] = eventsByMachineId[service['busId']] if service['busId'] in eventsByMachineId.keys() else []
        service['random'] = False

        try:
            busData = busassignment.getEstimatedLocation(stopCode, distance)
        except Exception as e:
            logger.error(str(e))
            busData = {'latitude': 500, 'longitude': 500, 'direction': 'I'}
            service['random'] = True

        service['tienePasajeros'] = 0
        service['lat'] = busData['latitude']
        service['lon'] = busData['longitude']
        service['direction'] = busData['direction']
        service['color'] = Service.objects.filter(
            service=service['servicio'], gtfs__version=settings.GTFS_VERSION).values_list('color_id', flat=True)[0]

        try:
            service['sentido'] = busassignment.getDirection(
                stopObj, distance)
        except Exception as e:
            logger.error(str(e))
            service['sentido'] = "left"

        authBuses.append(service)

    return authBuses


def mergeBuses(userBuses, authorityBuses):
    """ Join the list of user buses with authority buses """
    buses = []

    authBusesDict = {}
    for authBus in authorityBuses:
        licensePlate = authBus['patente'].upper()
        authBusesDict[licensePlate] = authBus

    for userBus in userBuses:
        # print "user bus: " + str(userBus['patente'])
        licensePlate = userBus['patente'].upper()
        if licensePlate == Constants.DUMMY_LICENSE_PLATE and \
                not userBus['isSameUser']:
            buses.append(userBus)
        elif licensePlate in authBusesDict.keys():
            authBus = authBusesDict[licensePlate]
            if authBus['servicio'] == userBus['servicio']:
                userBus['tiempo'] = authBus['tiempo']
                userBus['distancia'] = authBus['distancia']

                userBus['tiempoV2'] = authBus['tiempoV2']
                userBus['distanciaV2'] = authBus['distanciaV2']

                userBus['distanciaMts'] = authBus['distanciaMts']
                userBus['sentido'] = authBus['sentido']

                # if user who ask is the same of this user bus
                # will be omitted
                if not userBus['isSameUser']:
                    buses.append(userBus)
                authorityBuses.remove(authBus)

    buses = buses + authorityBuses

    return buses
