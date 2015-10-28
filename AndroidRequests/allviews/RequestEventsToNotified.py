from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone, dateparse
from django.core import serializers
from django.http import HttpResponse

#python utilities
import requests, json
import hashlib
import os
from random import random, uniform

# my stuff
# import DB's models
from AndroidRequests.models import *

class RequestEventsToNotified(View):
	"""This class sends the event that can be notified in at a given time,
	for examle if i'm on a busstop i can report some events regarding what i see,
	so i report things from the bustop and what i can see of the bus. If i'm on a bus
	i can report problems whit the bus with more detail."""

	def get(self, request, pWhich):
		
		events = []

		if pWhich == 'stopstop':
			events = Event.objects.filter(eventType='busStop')
		elif pWhich == 'stopbus':
			events = Event.objects.filter(eventType='bus', origin='o')
		elif pWhich == 'busbus':
			events = Event.objects.filter(eventType='bus', origin='i')

		response = []

		for data in events:
			responseAux = {}
			responseAux['name'] = data.name
			responseAux['description'] = data.description
			responseAux['lifespam'] = data.lifespam
			responseAux['category'] = data.category
			responseAux['origin'] = data.origin
			responseAux['eventType'] = data.eventType
			print responseAux
			response.append(responseAux)

		return JsonResponse(response, safe=False)



