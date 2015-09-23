from django.shortcuts import render
from django.http import JsonResponse
import requests, json


def nearBusStops(request, pLat, pLon):
	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
	params = {'location': str(pLat)+","+str(pLon),
			 'sensor': True,
			 'key': "AIzaSyDFxEVKnPKStiQoLMU0xm0ASXPfTzcmTno",
			 'rankby': "distance",
			 'types': "bus_station"}
	response = requests.get(url=url, params = params)
	data = json.loads(response.text)
	response = []
	for result in data["results"]:
		response.append({'name': result['name'], 
						 'location': {'lat': result['geometry']['location']['lat'], 
						 			  'lon': result['geometry']['location']['lng']}})
	return JsonResponse(response, safe=False)