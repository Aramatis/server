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
		bus = Bus.objects.get_or_create(registrationPlate = dato['patente'].replace("-", ""), \
										service = dato['servicio'])[0]
		busdata = bus.getLocation(dato['distancia'].replace(' mts.', ''))
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

class RequestToken(View):
	"""This class handles the start of the traking, asignin a token
	to identifie the trip, not the device."""

	def __init__(self):
		self.context={}

	def get(self, request, pBusService, pRegistrationPlate):
		data = timezone.now() # the token is primary a hash of the 
		salt = os.urandom(20) # time stamp plus a random salt
		hashToken = hashlib.sha512( str(data) + salt ).hexdigest()
		bus = Bus.objects.get_or_create(registrationPlate = pRegistrationPlate, \
		 service = pBusService)[0]
		aToken = Token.objects.create(token=hashToken, bus = bus, color=self.getRandomColor())
		ActiveToken.objects.create(timeStamp=data,token=aToken)

		# we store the active token
		response = {}
		response['token'] = hashToken

		return JsonResponse(response, safe=False)

	def getRandomColor(self):
		letters = '0123456789ABCDEF0'
		color = '#'
		colors = {'#2c7fb8','#dd1c77','#016c59','#de2d26','#d95f0e'}
		#for cont in range(6):
		#color += letters[int(round(random() * 16))]
		color = list(colors)[int(round(random() * 4))]
		return color		

class EndRoute(View):
	"""This class handles the ending of a trip tracking removing the token
	from the active token table."""
	def __init__(self):
		self.context={}

	def get(self, request, pToken):
		
		response = {}

		if ActiveToken.objects.filter(token=pToken).exists():
			aToken = ActiveToken.objects.get(token=pToken).delete()
			response['response'] = 'Trip ended.'
		else:#if the token was not found alert
			response['response'] = 'Token doesn\'t exist.'

		return JsonResponse(response, safe=False)

class SendPoses(View):
	"""This class recieves a segmente of the trajectory asociate to a token."""
	def __init__(self):
		self.context={}

	def get(self, request, pToken, pTrajectory):
		response = {}

		if ActiveToken.objects.filter(token=pToken).exists():
			trajectory = json.loads(pTrajectory)
			trajectory = trajectory['poses']

			#update the token time stamp, for maintanence purpuses
			aToken = ActiveToken.objects.get(token=pToken)
			aToken.timeStamp = timezone.now()
			aToken.save()

			theToken = Token.objects.get(token=pToken)

			for pose in trajectory:
				# set awareness to time stamp, to the server UTC
				aTimeStamp = dateparse.parse_datetime(pose['timeStamp'])

				aTimeStamp = timezone.make_aware(aTimeStamp)

				
				PoseInTrajectoryOfToken.objects.create(longitud=pose['longitud'],latitud=pose['latitud'],\
					 timeStamp=aTimeStamp, sender=pose["sender"],token=theToken)

			response['response'] = 'Poses were register.'
		else:#if the token was not found alert
			response['response'] = 'Token doesn\'t exist.'

		return JsonResponse(response, safe=False)

class RegisterEventBus(View):
	'''This class handles the requests that reports events of a bus'''

	def get(self, request, pBusID, pTimeStamp, pEventID, pConfirmDecline, pMessageOrigin):
		theEvent = Events.objects.get(id=pEventID)
		theBus = Bus.objects.get(service=pBusID)

		aTimeStamp = dateparse.parse_datetime(pTimeStamp)
		aTimeStamp = timezone.make_aware(aTimeStamp)

		oldestAlertedTime = aTimeStamp - timezone.timedelta(minutes=theEvent.lifespam)

		if EventForBus.objects.filter(timeStamp_gt = oldestAlertedTime, bus=theBus, event=theEvent).exist():
			eventReport = EventForBus.objects.get(timeStamp_gt = oldestAlertedTime, bus=theBus, event=theEvent)

			# updates to the event reported
			eventReport.timeStamp = aTimeStamp
			if pConfirmDecline == 'decline':
				eventReport.eventDecline += 1
			else:
				eventReport.eventConfirm += 1

			eventReport.save()
		else:
			aEventReport = EventForBus.objects.create(bus=theBus, event=theEvent, origin=pMessageOrigin, timeStamp=aTimeStamp)

			if pConfirmDecline == 'decline':
				aEventReport.eventDecline = 1
				aEventReport.eventConfirm = 0

			aEventReport.save()



		response['response'] = 'Thanks for the information, give to recieve.'
		return JsonResponse(response, safe=False)