from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone, dateparse

#python utilities
import requests, json
import hashlib
import os
from random import random

# my stuff
# import DB's models
from AndroidRequests.models import DevicePositionInTime, ActiveToken, PoseInTrajectoryOfToken

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
	return JsonResponse(data['servicios'], safe=False)

class RequestToken(View):
	"""This class handles the start of the traking, asignin a token
	to identifie the trip, not the device."""

	def __init__(self):
		self.context={}

	def get(self, request):
		data = timezone.now() # the token is primary a hash of the 
		salt = os.urandom(20) # time stamp plus a random salt
		hashToken = hashlib.sha512( str(data) + salt ).hexdigest()

		ActiveToken.objects.create(timeStamp=data,token=hashToken, color=self.getRandomColor())

		# we store the active token
		response = {}
		response['token'] = hashToken

		return JsonResponse(response, safe=False)

	def getRandomColor(self):
		letters = '0123456789ABCDEF0'
		color = '#'
		for cont in range(6):
			color += letters[int(round(random() * 16))]
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

			for pose in trajectory:
				# set awareness to time stamp, to the server UTC
				aTimeStamp = dateparse.parse_datetime(pose['timeStamp'])
				aTimeStamp = timezone.make_aware(aTimeStamp)

				PoseInTrajectoryOfToken.objects.create(longitud=pose['longitud'],latitud=pose['latitud'],\
					timeStamp=aTimeStamp,token=pToken,color=aToken.color)

			response['response'] = 'Poses were register.'
		else:#if the token was not found alert
			response['response'] = 'Token doesn\'t exist.'

		return JsonResponse(response, safe=False)