from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone, dateparse

#python utilities
import requests, json
import hashlib
import os

# my stuff
from AndroidRequests.models import DevicePositionInTime, ActiveToken, PoseInTrajactoryOfToken

def nearbyBusStops(request, pLat, pLon):
	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
	params = {'location': str(pLat)+","+str(pLon),
			 'sensor': True,
			 'key': "AIzaSyDFxEVKnPKStiQoLMU0xm0ASXPfTzcmTno",
			 'rankby': "distance",
			 'types': "bus_station"}

	# the pose is stored

	currPose = DevicePositionInTime(longitud = pLon, latitud = pLat \
	,timeStamp = timezone.now())
	currPose.save()

	response = requests.get(url=url, params = params)
	data = json.loads(response.text)
	response = []
	for result in data["results"]:
		response.append({'name': result['name'], 
						 'location': {'lat': result['geometry']['location']['lat'], 
						 			  'lon': result['geometry']['location']['lng']}})
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
		print 'lolol'
		ActiveToken.objects.create(timeStamp=data,tocken=hashToken)

		# we store the active token
		response = {}
		response['toekn'] = hashToken

		print response
		return JsonResponse(response, safe=False)
		

class EndRoute(View):
	"""This class handles the ending of a trip tracking removing the token
	from the active token table."""
	def __init__(self):
		self.context={}

	def get(self, request, pToken):
		
		response = {}

		if ActiveToken.objects.filter(tocken=pToken).exists():
			aToken = ActiveToken.objects.get(tocken=pToken).delete()
			response['response'] = 'Trip ended.'
		else:#if the token was not found alert
			response['response'] = 'token doesn\'t exist.'

		return JsonResponse(response, safe=False)

class SendPoses(View):
	"""This class recieves a segmente of the trajectory asociate to a token."""
	def __init__(self):
		self.context={}

	def get(self, request, pToken, pTrajectory):
		response = {}


		print pTrajectory
		if ActiveToken.objects.filter(tocken=pToken).exists():
			trajectory = json.loads(pTrajectory)
			trajectory = trajectory['poses']
			for pose in trajectory:
				PoseInTrajactoryOfToken.objects.create(longitud=pose['longitud'],latitud=pose['latitud'],\
					timeStamp=dateparse.parse_datetime(pose['timeStamp']),tocken=pToken)

			response['response'] = 'Poses were register.'
		else:#if the token was not found alert
			response['response'] = 'token doesn\'t exist.'

		return JsonResponse(response, safe=False)