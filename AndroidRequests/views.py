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
	for dato in data['servicios']:
		if(dato["valido"]!=1):
			continue
		bus = Bus.objects.get_or_create(registrationPlate = dato['patente'].replace("-", ""), \
										service = dato['servicio'])[0]
		busdata = bus.getLocation(data['id'], dato['distancia'].replace(' mts.', ''))
		dato['hasPassenger'] = 0 if busdata['estimated'] else 1
		dato['lat'] = busdata['latitud']
		dato['lon'] = busdata['longitud']
		servicios.append(dato)
	#Eventos dummy
	eventos = []

	evento1 = {}
	evento1["id"] = "npi"
	evento1["descripcion"] = "Paradero lleno"

	evento2 = {}
	evento2["id"] = "ble"
	evento2["descripcion"] = "Paradero roto"

	eventos.append(evento1)
	eventos.append(evento2)

	response = {}
	response["servicios"] = servicios
	response["eventos"] = eventos
	return JsonResponse(response, safe=False)
