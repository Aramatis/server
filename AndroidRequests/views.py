from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone

from collections import defaultdict

from AndroidRequests.encoder import TranSappJSONEncoder
from AndroidRequests.allviews.EventsByBusStop import EventsByBusStop
from AndroidRequests.allviews.EventsByBusV2 import EventsByBusV2
from AndroidRequests.models import DevicePositionInTime, BusStop, NearByBusesLog, Busv2, Busassignment, Service, \
    ServicesByBusStop, Token

import AndroidRequests.constants as constants

import json
import logging
import re
import requests


def userPosition(request, pPhoneId, pLat, pLon):
    """
    This function stores the pose of an active user
    :param request: django request object
    :param pPhoneId: phone identifier (uuid)
    :param pLat: latitude
    :param pLon: longitude
    :return: json
    """

    DevicePositionInTime.objects.create(
        longitude=pLon,
        latitude=pLat,
        timeStamp=timezone.now(),
        phoneId=pPhoneId)

    response = {'response': 'Pose registered.'}
    return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)


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
    userBuses = get_user_buses(stopObj, pPhoneId)

    """
    DTPM BUSES
    """
    # DTPM source
    IP = "18.231.23.145"
    url = "http://{}/dtpm/busStopInfo/".format(IP)
    url = "{}{}/{}".format(url, settings.SECRET_KEY, pBusStop)
    response = requests.get(url=url)

    authBuses = []
    if response.text != "":
        data = json.loads(response.text)

        if 'id' in data:
            authBuses = get_authority_buses(stopObj, data)

        if data['error'] is not None:
            answer['DTPMError'] = data['error']
        else:
            answer['DTPMError'] = ""

        """
        ADDED ADDITIONAL INFO OF ROUTES
        """
        if "routeInfo" in data.keys():
            answer["routeInfo"] = data["routeInfo"]

    """
    MERGE USER BUSES WITH DTPM BUSES
    """
    answer['servicios'] = merge_buses(userBuses, authBuses)

    return JsonResponse(answer, safe=False, encoder=TranSappJSONEncoder)


def format_service_name(serviceName):
    """ apply common format used by transantiago to show service name to user  """
    if not serviceName[-1:] == 'N':
        serviceName = "{}{}".format(serviceName[0], serviceName[1:].lower())
    return serviceName


def format_distance(distance):
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


def format_time(time, distance):
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


def get_user_buses(stop_obj, questioner):
    """
    Get active user buses
    :param stop_obj: stop object
    :param questioner: phone identifier who ask
    :return: list of user buses
    """

    logger = logging.getLogger(__name__)

    servicesToBusStop = ServicesByBusStop.objects.select_related('service'). \
        filter(busStop=stop_obj, gtfs__version=settings.GTFS_VERSION).values_list('service__service', 'code')
    route_names = []
    route_directions = []
    for route, route_with_direction in servicesToBusStop:
        route_names.append(route)
        route_directions.append(route_with_direction.replace(route, ""))

    # active user buses that stop in the bus stop
    active_user_buses = Token.objects.select_related('tranSappUser__level').\
        prefetch_related("busassignment__uuid__busassignment_set").filter(
        busassignment__service__in=route_names,
        activetoken__isnull=False)

    # retrieve events for all user buses and busassignments related
    bus_assignments = []
    for token_obj in active_user_buses:
        bus_assignments += token_obj.busassignment.uuid.busassignment_set.all()
    events_by_machine_id = EventsByBusV2().getEventsForBuses(bus_assignments, timezone.now())

    global_scores = []
    # used to choose which bus avatar shows. Criteria: user with highest global score
    user_buses = []
    uuids = []
    # bus identifiers
    for token_obj in active_user_buses:
        service_index = route_names.index(token_obj.busassignment.service)
        machine_id = token_obj.busassignment.uuid.uuid

        if machine_id in uuids:
            position = uuids.index(machine_id)
            bus = user_buses[position]
            if str(token_obj.phoneId) == questioner:
                bus['isSameUser'] = True
            # update avatar id
            if token_obj.tranSappUser is not None:
                global_score = token_obj.tranSappUser.globalScore
                if global_scores[position] < global_score:
                    global_scores[position] = global_score
                    bus['avatarId'] = token_obj.tranSappUser.busAvatarId
                    bus['user'] = token_obj.tranSappUser.getDictionary()

            user_buses[position] = bus

        elif token_obj.direction == route_directions[service_index]:

            bus = {'servicio': token_obj.busassignment.service,
                   'patente': token_obj.busassignment.uuid.registrationPlate,
                   'direction': token_obj.direction,
                   'isSameUser': True if str(token_obj.phoneId) == questioner else False}

            global_score = 0
            # default bus avatar id
            bus['avatarId'] = 1
            if token_obj.tranSappUser is not None:
                global_score = token_obj.tranSappUser.globalScore
                bus['avatarId'] = token_obj.tranSappUser.busAvatarId
                bus['user'] = token_obj.tranSappUser.getDictionary()

            bus_data = token_obj.busassignment.getLocation()
            bus['random'] = bus_data['random']
            bus['lat'] = bus_data['latitude']
            bus['lon'] = bus_data['longitude']
            bus['tienePasajeros'] = bus_data['passengers']

            bus['eventos'] = events_by_machine_id[machine_id] if machine_id in events_by_machine_id.keys() else []

            try:
                # assume that bus is 30 meters from bus stop to predict direction
                bus['sentido'] = token_obj.busassignment.getDirection(
                    stop_obj, 30)
            except Exception as e:
                logger.error(str(e))
                bus['sentido'] = "left"

            bus['color'] = Service.objects.filter(service=bus['servicio'], gtfs__version=settings.GTFS_VERSION). \
                values_list("color_id", flat=True)[0]
            bus['valido'] = 1
            # extras
            # old version, 1.2.17 and previous
            bus['tiempo'] = 'Viajando'
            distance = token_obj.get_distance_to(stop_obj.longitude, stop_obj.latitude)
            bus['distancia'] = distance
            # new version, 1.4.23 and upper
            bus['tiempoV2'] = 'Viajando'
            bus['distanciaV2'] = format_distance(distance)
            bus['distanciaMts'] = distance
            # add new param 'uuid'
            bus['busId'] = machine_id

            if not bus['random']:
                user_buses.append(bus)
                uuids.append(machine_id)
                global_scores.append(global_score)

    return user_buses


def get_authority_buses(stop_obj, data):
    """
    Apply json format to authority info
    :param stop_obj: stop object
    :param data: data given by authority of public transport system
    :return: authority bus list
    """

    logger = logging.getLogger(__name__)

    auth_buses = []
    stop_code = data['id']

    """
    Generate busObjDict and busDict dicts to make just two queries to get all buses info
    """
    route_list = filter(lambda route: route['patente'] is not None, data['servicios'])
    license_plate_list = map(lambda route: route['patente'], route_list)

    busObjList = Busv2.objects.prefetch_related('busassignment_set').filter(registrationPlate__in=license_plate_list)
    busObjDict = defaultdict(None)
    for bus_obj in busObjList:
        busObjDict[bus_obj.registrationPlate] = bus_obj

    bus_list = Busv2.objects.filter(registrationPlate__in=license_plate_list).values_list('registrationPlate',
                                                                                          'uuid',
                                                                                          'busassignment__service')
    busDict = defaultdict(lambda: {'busassignments': [], 'uuid': None})
    for license_plate, uuid, route in bus_list:
        busDict[license_plate]['busassignments'].append(route)
        busDict[license_plate]['uuid'] = uuid

    """
    Generate eventBusObjDict dict to make one query to get all event buses info
    """
    busassignments = []
    for bus_obj in busObjList:
        busassignments += bus_obj.busassignment_set.all()
    events_by_machine_id = EventsByBusV2().getEventsForBuses(busassignments, timezone.now())

    for service in data['servicios']:
        if service['valido'] != 1 or service['patente'] is None \
                or service['tiempo'] is None or service['distancia'] == 'None mts.':
            continue
        # clean the strings from spaces and unwanted format
        service['servicio'] = format_service_name(service['servicio'])
        distance = int(service['distancia'].replace(' mts.', ''))
        service['distanciaMts'] = distance
        service['distanciaV2'] = format_distance(distance)
        service['tiempoV2'] = format_time(service['tiempo'], distance)

        # default avatar id = 0
        service['avatarId'] = 0

        license_plate = service['patente']
        route = service['servicio']
        # request the correct bus
        if license_plate not in busDict.keys():
            bus = Busv2.objects.create(registrationPlate=license_plate)
            service['busId'] = bus.uuid
            busassignment = Busassignment.objects.create(service=route, uuid=bus)
        else:
            service['busId'] = busDict[service['patente']]['uuid']
            if route not in busDict[license_plate]['busassignments']:
                busassignment = Busassignment.objects.create(service=route, uuid=busObjDict[license_plate])
            else:
                # this uses prefetch related made in busObjList
                busassignment = [b for b in busObjDict[license_plate].busassignment_set.all() if b.service == route][0]

        service['eventos'] = events_by_machine_id[service['busId']] if service[
                                                                           'busId'] in events_by_machine_id.keys() else []
        service['random'] = False

        try:
            bus_data = busassignment.getEstimatedLocation(stop_code, distance)
        except Exception as e:
            logger.error("Trying to get estimated location: " + str(e))
            bus_data = {'latitude': 500, 'longitude': 500, 'direction': 'I'}
            service['random'] = True

        service['tienePasajeros'] = 0
        service['lat'] = bus_data['latitude']
        service['lon'] = bus_data['longitude']
        service['direction'] = bus_data['direction']
        service['color'] = Service.objects.filter(
            service=service['servicio'], gtfs__version=settings.GTFS_VERSION).values_list('color_id', flat=True)[0]

        try:
            service['sentido'] = busassignment.getDirection(
                stop_obj, distance)
        except Exception as e:
            logger.error(str(e))
            service['sentido'] = "left"

        auth_buses.append(service)

    return auth_buses


def merge_buses(user_buses, authority_buses):
    """
    Join the list of user buses with authority buses
    :param user_buses: user bus list
    :param authority_buses: authority bus list
    :return: union of user bus list and authority bus list
    """
    buses = []

    auth_buses_dict = {}
    for auth_bus in authority_buses:
        license_plate = auth_bus['patente'].upper()
        auth_buses_dict[license_plate] = auth_bus

    for user_bus in user_buses:
        # print "user bus: " + str(user_bus['patente'])
        license_plate = user_bus['patente'].upper()
        if license_plate == constants.DUMMY_LICENSE_PLATE and \
                not user_bus['isSameUser']:
            buses.append(user_bus)
        elif license_plate in auth_buses_dict.keys():
            auth_bus = auth_buses_dict[license_plate]
            if auth_bus['servicio'] == user_bus['servicio']:
                user_bus['tiempo'] = auth_bus['tiempo']
                # user_bus['distancia'] = auth_bus['distancia']

                user_bus['tiempoV2'] = auth_bus['tiempoV2']
                # user_bus['distanciaV2'] = auth_bus['distanciaV2']

                #user_bus['distanciaMts'] = auth_bus['distanciaMts']
                user_bus['sentido'] = auth_bus['sentido']

                # if user who ask is the same of this user bus
                # will be omitted
                if not user_bus['isSameUser']:
                    buses.append(user_bus)
                authority_buses.remove(auth_bus)

    buses = buses + authority_buses

    return buses
