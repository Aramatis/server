from django.shortcuts import render
from django.http import JsonResponse
import requests, json

from django.utils import timezone

from AndroidRequests.models import DevicePositionInTime

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
	print currPose.timeStamp

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

#class GiveDevicePose(object):
#	"""This class recives a pose from a given device"""
#	def __init__(self, arg):
#		'''The data to pass to the html template'''
##
#	def get(self, requests, longitud, latitud, dateTime):
#		'''Recieves logitud an latitud from devies and the time the measurmet was made'''
###		
#		return JsonResponse(response, safe=False)
		