# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
                                                                                        'longitude', 'userRouteCode')

    for location in locations:
        answer[location[0]] = {
            "latitude": location[1],
            "longitude": location[2],
            "direction": get_direction(location[3]),
            "route": get_user_route(location[3])
        }

    return answer
