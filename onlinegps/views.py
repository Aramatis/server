# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone

from AndroidRequests.gpsFunctions import haversine

from onlinegps.models import LastGPS

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


def get_locations(license_plate_list):
    """ retrieve location based on license plate """

    answer = {}
    locations = LastGPS.objects.filter(licensePlate__in=license_plate_list).values_list('licensePlate', 'latitude',
                                                                                        'longitude', 'userRouteCode',
                                                                                        'timestamp')

    for location in locations:
        answer[location[0]] = {
            "latitude": location[1],
            "longitude": location[2],
            "direction": get_direction(location[3]),
            "route": get_user_route(location[3]),
            "timestamp": location[4]
        }

    return answer


def is_near_to_bus_position(licensePlate, positions):
    """
    Check if time nearest in positions has distance with last gps point greater than max_distance meters
    @return boolean -> True: i don't know anything, False: user bus is far away from real bus
    """
    assert len(positions) > 0, "positions is a empty list"

    max_seconds = 10
    max_distance_mts = 500

    info = get_locations([licensePlate])

    if licensePlate in info.keys():
        machineInfo = get_locations([licensePlate])[licensePlate]
    else:
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