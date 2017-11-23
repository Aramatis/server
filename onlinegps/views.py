# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone

from AndroidRequests.gpsFunctions import haversine

from onlinegps.models import LastGPS

import time

DIRECTIONS = ["I", "R"]


def get_direction(user_route):
    """ identify bus direction based on user route """
    if len(user_route) < 2:
        return None

    # delete first 3 letter (all user routes have this)
    direction = user_route[3:]

    if direction[0] in DIRECTIONS:
        return direction[0]
    elif direction[1] in DIRECTIONS:
        return direction[1]

    return None


def get_user_route(user_route):
    """ delete code that is not known by users """
    if len(user_route) < 2:
        return None

    if user_route[3] in DIRECTIONS:
        return user_route[:3]
    elif user_route[4] in DIRECTIONS:
        return user_route[:4]

    return None


def get_machine_locations(license_plates):
    """ retrieve location based on license plate """
    is_list = False
    location_query = LastGPS.objects
    if isinstance(license_plates, list):
        location_query = location_query.filter(licensePlate__in=license_plates)
        is_list = True
    else:
        location_query = location_query.filter(licensePlate=license_plates)
    location_query = location_query.values_list('licensePlate', 'latitude',
                                                'longitude', 'userRouteCode',
                                                'timestamp')
    if location_query.count() == 0:
        # maybe the data is loading, so we wait a little bit
        time.sleep(0.06)

    answer = {}
    for location in location_query:
        answer[location[0]] = {
            "latitude": location[1],
            "longitude": location[2],
            "direction": get_direction(location[3]),
            "route": get_user_route(location[3]),
            "timestamp": location[4]
        }

    if len(answer.keys())==0:
        return None
    elif is_list:
        return answer
    else:
        return answer[license_plates]


def get_real_machine_info_with_distance(registrationPlate, longitude, latitude):

    longitude = None
    latitude = None
    time = None
    distance = None

    machine_info = get_machine_locations(registrationPlate)
    if machine_info is not None:
        longitude = machine_info["longitude"]
        latitude = machine_info["latitude"]
        time = machine_info["timestamp"]
        distance = haversine(longitude, latitude, longitude, latitude)

    return longitude, latitude, time, distance


def is_near_to_bus_position(licensePlate, positions):
    """
    Check if time nearest in positions has distance with last gps point greater than max_distance meters
    @return boolean -> True: i don't know anything, False: user bus is far away from real bus
    """
    assert len(positions) > 0, "positions is a empty list"

    max_seconds = 10
    max_distance_mts = 500

    machineInfo = get_machine_locations(licensePlate)

    if machineInfo is None:
        return True

    nearestPosition = None
    diffTime = timezone.timedelta(days=700)

    for index, position in enumerate(positions):
        currentDiffTime = abs(machineInfo["timestamp"] - position[2])
        if currentDiffTime < diffTime:
            diffTime = currentDiffTime
            nearestPosition = position

    distance = haversine(machineInfo['longitude'], machineInfo['latitude'],
                         nearestPosition[0], nearestPosition[1])
    if diffTime.total_seconds() < max_seconds and distance > max_distance_mts:
        # break trip
        return False

    # in any other case don't do anything
    return True
