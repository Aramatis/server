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

class RegisterEventBusStop(View):
	'''This class handles the requests that reports events of a busstop'''

	def get(self, request, pBusStopCode, pTimeStamp, pEventID, pConfirmDecline):
		response = {}
		theEvent = Event.objects.get(id=pEventID)
		theBusStop = BusStop.objects.get(code=pBusStopCode)

		aTimeStamp = dateparse.parse_datetime(pTimeStamp)
		aTimeStamp = timezone.make_aware(aTimeStamp)

		oldestAlertedTime = aTimeStamp - timezone.timedelta(minutes=theEvent.lifespam)

		if EventForBusStop.objects.filter(timeStamp__gt = oldestAlertedTime, busStop=theBusStop, event=theEvent).exists():
			eventsReport = EventForBusStop.objects.filter(timeStamp__gt = oldestAlertedTime, busStop=theBusStop, event=theEvent)
			eventReport = self.getLastEvent(eventsReport)
			# updates to the event reported
			eventReport.timeStamp = aTimeStamp
			if pConfirmDecline == 'decline':
				eventReport.eventDecline += 1
			else:
				eventReport.eventConfirm += 1

			eventReport.save()
		else:
			aEventReport = EventForBusStop.objects.create(busStop=theBusStop, event=theEvent, timeStamp=aTimeStamp, timeCreation=aTimeStamp)
			

			if pConfirmDecline == 'decline':
				aEventReport.eventDecline = 1
				aEventReport.eventConfirm = 0

			aEventReport.save()



		response['response'] = 'Thanks for the information, give to recieve.'
		return JsonResponse(response, safe=False)

	def getLastEvent(self, querySet):
		toReturn = querySet[0]

		for val in range(len(querySet)-1):
			if toReturn.timeStamp < val.timeStamp:
				toReturn = val

		return toReturn