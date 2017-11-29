from django.conf import settings
from cache.cache_decorator import cache_for

from gtfs.models import ServicesByBusStop, ServiceLocation, ServiceStopDistance
from gtfs.exceptions import RouteDoesNotStopInBusStop, RouteDistanceNotFoundException, RouteNotFoundException, \
    ThereIsNotClosestLocation

import logging

day_in_seconds = 60 * 24
month_in_seconds = 30 * day_in_seconds


@cache_for(month_in_seconds)
def get_direction(stop_obj, route, distance):
    """ Given a bus stop and the distance from the bus to the bus stop,
        return the address to which point the bus """
    try:
        route_code = ServicesByBusStop.objects.get(busStop=stop_obj, service__service=route,
                                                   gtfs__version=settings.GTFS_VERSION).code
    except ServicesByBusStop.DoesNotExist:
        raise RouteNotFoundException(
            "Service {} is not present in bus stop {}".format(route, stop_obj.code))

    try:
        route_distance = ServiceStopDistance.objects.get(busStop=stop_obj, service=route_code,
                                                         gtfs__version=settings.GTFS_VERSION).distance
    except ServiceStopDistance.DoesNotExist:
        raise RouteDistanceNotFoundException(
            "The distance is not possible getting for bus stop '{}' and service '{}'".format(stop_obj.code,
                                                                                             route_code))

    distance = route_distance - int(distance)
    greaters = ServiceLocation.objects.filter(service=route_code, distance__gt=distance,
                                              gtfs__version=settings.GTFS_VERSION).order_by('distance')[:1]
    lowers = ServiceLocation.objects.filter(service=route_code, distance__lte=distance,
                                            gtfs__version=settings.GTFS_VERSION).order_by('-distance')[:1]

    # we need two point to detect the bus direction (left, right, up, down)
    if len(greaters) > 0 and len(lowers) > 0:
        greater = greaters[0]
        lower = lowers[0]
    elif len(greaters) == 0 and len(lowers) == 2:
        greater = lowers[0]
        lower = lowers[1]
    elif len(greaters) == 0 and len(lowers) == 1:
        greater = lowers[0]
        lower = lowers[0]
    elif len(lowers) == 0 and len(greaters) == 2:
        lower = greaters[0]
        greater = greaters[1]
    elif len(lowers) == 0 and len(greaters) == 1:
        lower = greaters[0]
        greater = greaters[0]
    elif len(lowers) == 0 and len(greaters) == 2:
        lower = greaters[0]
        greater = greaters[1]
    elif len(greaters) == 0 and len(lowers) == 0:
        # there are not points to detect direction
        logger = logging.getLogger(__name__)
        logger.info("There is not position to detect bus direction")
        return "left"

    epsilon = 0.00008
    x1 = lower.longitude
    # y1 = lower.latitude
    x2 = greater.longitude
    # y2 = greater.latitude

    if abs(x2 - x1) >= epsilon:
        if x2 - x1 > 0:
            return "right"
        else:
            return "left"
    else:
        # we compare bus location with bus stop location
        x_bus_stop = stop_obj.longitude
        if x2 - x_bus_stop > 0:
            return "left"
        else:
            return "right"


@cache_for(month_in_seconds)
def get_estimated_location(stop_code, route, distance):
    """ Given a distance from the bus to the bus stop, this method returns the global position of the machine. """
    try:
        route_code = ServicesByBusStop.objects.filter(busStop__code=stop_code, service__service=route,
                                                      gtfs__version=settings.GTFS_VERSION).only('code').first().code
    except AttributeError:
        raise RouteNotFoundException("Service {} is not present in bus stop {}".format(route, stop_code))

    try:
        ssd = ServiceStopDistance.objects.filter(
            busStop__code=stop_code, service=route_code,
            gtfs__version=settings.GTFS_VERSION).only('distance').first().distance - int(distance)
    except AttributeError:
        raise RouteDoesNotStopInBusStop(
            "route({0}) and bus stop({1}) does not match in ServiceStopDistance".format(route_code, stop_code))

    closest_gt_obj = ServiceLocation.objects.filter(service=route_code, gtfs__version=settings.GTFS_VERSION,
                                                    distance__gte=ssd).order_by('distance').first()
    closest_gt = closest_gt_obj.distance if closest_gt_obj is not None else 50000

    closest_lt_obj = ServiceLocation.objects.filter(service=route_code, gtfs__version=settings.GTFS_VERSION,
                                                    distance__lte=ssd).order_by('-distance').first()
    closest_lt = closest_lt_obj.distance if closest_lt_obj is None else 0

    if abs(closest_gt - ssd) < abs(closest_lt - ssd):
        closest_location = closest_gt_obj
    else:
        closest_location = closest_lt_obj

    if closest_location is None:
        raise ThereIsNotClosestLocation(
            "There is not exist closest location with distance {}, route {} and bus stop {}".format(distance,
                                                                                                    route_code,
                                                                                                    stop_code))

    return {
        'latitude': closest_location.latitude,
        'longitude': closest_location.longitude,
        'direction': route_code[-1]
    }
