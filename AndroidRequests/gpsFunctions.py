import AndroidRequests.constants as Constants
from django.utils.dateparse import parse_datetime

from math import radians, cos, sin, asin, sqrt
import urllib2
import json


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    m = km * 1000
    return m


def getGPSData(registrationPlate, timeStamp, plon, plat, jsonContent=None):
    parameters = {}
    parameters['licencePlate'] = registrationPlate
    parameters['time'] = timeStamp.strftime(
        "%Y-%m-%d %H:%M:%S").replace(" ", "%20")
    url = "http://200.9.100.91:8080/gpsonline/transappBusPosition/getEstimatedPosition"
    full_url = url + '?licencePlate=' + \
        parameters['licencePlate'] + '&time=' + parameters['time']

    longitud = None
    latitud = None
    time = None
    distance = None

    try:
        if jsonContent is not None:
            response = json.loads(jsonContent)
        else:
            data = urllib2.urlopen(full_url)
            response = json.load(data)
        if response['error'] is False and response['machine'][
                'licencePlate'] == parameters['licencePlate']:
            longitud = response['nearestGpsPoint']['longitude']
            latitud = response['nearestGpsPoint']['latitude']
            time = response['nearestGpsPoint']['time']
            time = parse_datetime(time + Constants.TIMEZONE)
            distance = haversine(longitud, latitud, plon, plat)
    except:
        pass

    return longitud, latitud, time, distance
