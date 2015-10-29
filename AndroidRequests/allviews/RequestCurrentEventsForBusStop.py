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

class RequestCurrentEventsForBusStop(View):
	"""This class gives the response to requesting the current
	reported events for a given busstop."""

	def get(self, resquest, pTimeStamp, pBusStopCode):

		aTimeStamp = dateparse.parse_datetime(pTimeStamp)
		aTimeStamp = timezone.make_aware(aTimeStamp)

		events = Event.objects.filter(eventType='busStop')
		theBusStop = BusStop.objects.get(code=pBusStopCode)

		response = self.getEventsForBusStop(theBusStop, events, aTimeStamp)
		
		return JsonResponse(response, safe=False)

	def getEventsForBusStop(self, pBusStop, pEvents, pTimeStamp):
		'''this method returns all the events that are reported for a specific timestamp.'''

		currentEventReport = []

		for event in pEvents:
			print '..'
			print pTimeStamp
			print event.lifespam
			eventTime = pTimeStamp - timezone.timedelta(minutes=event.lifespam)
			print eventTime
			aux = EventForBusStop.objects.filter(busStop=pBusStop,event=event,timeStamp__gt=eventTime)#.order_by('-timeStamp')
			for auxx in aux:
				print auxx.timeStamp

			if aux.exists():
				currentEventReport.append(aux[0].getDictionary())

		return currentEventReport

		

