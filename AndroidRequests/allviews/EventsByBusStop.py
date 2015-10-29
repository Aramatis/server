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

class EventsByBusStop(View):
	"""This class gives the response to requesting the current
	reported events for a given busstop."""

	def get(self, resquest, pBusStopCode):
		aTimeStamp = timezone.now()		
		theBusStop = BusStop.objects.get(code=pBusStopCode)

		eventsData = self.getEventsForBusStop(theBusStop, aTimeStamp)

		eventeDictionary = pBusStop.getDictionary()
		eventeDictionary['events'] = eventsData
		
		return JsonResponse(eventeDictionary, safe=False)

	def getEventsForBusStop(self, pBusStop, pTimeStamp):
		'''this method returns all the events that are reported for a specific timestamp.'''

		currentEventReport = []

		events = Event.objects.filter(eventType='busStop')
		for event in events:

			eventTime = pTimeStamp - timezone.timedelta(minutes=event.lifespam)
			aux = EventForBusStop.objects.filter(busStop=pBusStop,event=event,timeStamp__gt=eventTime).order_by('-timeStamp')

			if aux.exists():
				currentEventReport.append(aux[0].getDictionary())

		
		
		return currentEventReport
