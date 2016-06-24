from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone, dateparse

#python utilities
import requests, json
import hashlib
import os
from random import random, uniform

# my stuff
# import DB's models
from AndroidRequests.models import *
from AndroidRequests.allviews.EventsByBusStop import *
from AndroidRequests.allviews.EventsByBus import *
from AndroidRequests.predictorTranSantiago.WebService import *

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

    register = NearByBusesLog(userId = pUserId, busStop = theBusStop, timeStamp = timeNow)
    register.save()
    """ register user request """

    servicios = []
    getEventsBusStop = EventsByBusStop()
    busStopEvent = getEventsBusStop.getEventsForBusStop(theBusStop, timeNow)

    # for dev purpose
    # OBS: there isn't garanty about this url. it is third-party url

    url = "http://dev.adderou.cl/transanpbl/busdata.php"
    params = {'paradero': pBusStop}
    response = requests.get(url=url, params = params)

    if(response.text==""):
        response = {}
        response["servicios"] = servicios
        response["eventos"] = busStopEvent
        return JsonResponse(response, safe=False)

    data = json.loads(response.text)
    data['error'] = None

    # DTPM source
    #ws = WebService(request)
    #data = ws.askForServices(pBusStop)

    busStopCode=data['id']

    for dato in data['servicios']:
        if(dato["valido"]!=1):
            continue
        # clean the strings from spaces and unwanted format
        dato['servicio']  = dato['servicio'].strip()
        dato['patente']   = dato['patente'].replace("-", "")
        dato['patente']   = dato['patente'].strip()
        dato['servicio']  = dato['servicio'][0:].lower()
        distance = dato['distancia'].replace(' mts.', '')

        # request the correct bus
        bus = Bus.objects.get_or_create(registrationPlate = dato['patente'], \
                service = dato['servicio'])[0]
        busdata = bus.getLocation(busStopCode, distance)
        dato['tienePasajeros'] = busdata['passengers']
        dato['lat'] = busdata['latitud']
        dato['lon'] = busdata['longitud']
        dato['random'] = busdata['random']
        #TODO: log unregistered services
        dato['color'] = Service.objects.get(service=dato['servicio']).color_id
        dato['sentido'] = bus.getDirection(busStopCode, distance)

        getEventBus = EventsByBus()

        busEvents = getEventBus.getEventForBus(bus)

        dato['eventos'] = busEvents

        servicios.append(dato)

    response = {}
    if data['error'] != None:
        response['error'] = data['error']
    response["servicios"] = servicios
    response["eventos"] = busStopEvent
    return JsonResponse(response, safe=False)
