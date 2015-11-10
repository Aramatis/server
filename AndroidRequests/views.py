from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone, dateparse

#python utilities
import requests, json
import hashlib
import os
from random import random, uniform
import requests
# my stuff
# import DB's models
from AndroidRequests.models import *
from AndroidRequests.allviews.EventsByBusStop import *
from AndroidRequests.allviews.EventsByBus import *

def userPosition(request, pLat, pLon):
	'''This function stores the pose of an active user'''
	# the pose is stored
	currPose = DevicePositionInTime(longitud = pLon, latitud = pLat \
	,timeStamp = timezone.now())
	currPose.save()

	response = {'response':'Pose register.'}
	return JsonResponse(response, safe=False)

def nearbyBuses(request, pBusStop):
	url = "http://dev.adderou.cl/transanpbl/busdata.php"
	params = {'paradero': pBusStop}
	response = requests.get(url=url, params = params)
	data = json.loads(response.text)
	servicios = []

	timeNow = timezone.now()
	theBusStop = BusStop.objects.get(code=pBusStop)
	getEventsBusStop = EventsByBusStop()
	busStopEvent = getEventsBusStop.getEventsForBusStop(theBusStop, timeNow)
	closerDist = 10000
	time = ""
	for dato in data['servicios']:
		if(dato["valido"]!=1):
			continue

		distance = dato['distancia'].replace(' mts.', '')
		if (int(distance)<closerDist):
			closerDist = int(distance)
			time = dato['tiempo']
		dato['servicio'] = dato['servicio'].strip()
		dato['servicio'] = dato['servicio'][0] + dato['servicio'][1:].lower()
		bus = Bus.objects.get_or_create(registrationPlate = dato['patente'].replace("-", ""), \
										service = dato['servicio'])[0]
		busdata = bus.getLocation(pBusStop, distance)
		dato['tienePasajeros'] = 0 if busdata['estimated'] else 1
		dato['lat'] = busdata['latitud']
		dato['lon'] = busdata['longitud']
		dato['random'] = busdata['random']

		getEventBus = EventsByBus()
		busEvents = getEventBus.getEventForBus(bus)

		dato['eventos'] = busEvents

		servicios.append(dato)

	if(pBusStop=="PD1359"):
		for dato in data['servicios']:
			r = requests.get("http://200.9.100.91:8080/android/reportEventBus/" + dato['servicio'] + "/" + dato['patente'] + "/evn00201/confirm")

		dato = {}
		dato['servicio'] = "506"
		dato['patente'] = "AA0000"
		dato['distancia'] = str(closerDist) + " mts."
		bus = Bus.objects.get_or_create(registrationPlate = dato['patente'], service = dato['servicio'])[0]
		busdata = bus.getLocation(pBusStop, closerDist + 20)
		dato['tienePasajeros'] = 0 if busdata['estimated'] else 1
		dato['lat'] = busdata['latitud']
		dato['lon'] = busdata['longitud']
		dato['random'] = busdata['random']
		getEventBus = EventsByBus()
		busEvents = getEventBus.getEventForBus(bus)

		dato['eventos'] = busEvents

		servicios.append(dato)
	response = {}
	response["servicios"] = servicios
	response["eventos"] = busStopEvent
	return JsonResponse(response, safe=False)
