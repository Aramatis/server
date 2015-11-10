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

class RegisterEventBus(View):
	'''This class handles the requests that reports events of a bus'''

	def get(self, request, pBusService, pBusPlate, pEventID, pConfirmDecline):
		response = {}

		# here we request all the info needed to preoced
		aTimeStamp = timezone.now()
		theEvent = Event.objects.get(id=pEventID)
		theBus = Bus.objects.get_or_create(service=pBusService, registrationPlate=pBusPlate)[0]

		# estimate the oldest time where the reported event can be usefull
		# if there is no event here a new one is created
		oldestAlertedTime = aTimeStamp - timezone.timedelta(minutes=theEvent.lifespam)

		# check id there id an event
		if EventForBus.objects.filter(timeStamp__gt = oldestAlertedTime, bus=theBus, event=theEvent).exists():
			# get the event
			eventsReport = EventForBus.objects.filter(timeStamp__gt = oldestAlertedTime, bus=theBus, event=theEvent)
			eventReport = self.getLastEvent(eventsReport)

			# updates to the event reported
			eventReport.timeStamp = aTimeStamp

			# update the counters
			if pConfirmDecline == 'decline':
				eventReport.eventDecline += 1
			else:
				eventReport.eventConfirm += 1

			# save changes
			eventReport.save()
		else:
			# if an event was not found, create a new one
			aEventReport = EventForBus.objects.create(bus=theBus, event=theEvent, timeStamp=aTimeStamp,timeCreation=aTimeStamp)
			
			# set the initial values for this fiels
			if pConfirmDecline == 'decline':
				aEventReport.eventDecline = 1
				aEventReport.eventConfirm = 0

			aEventReport.save()



		response['response'] = 'Thanks for the information, give to recieve.'
		return JsonResponse(response, safe=False)

	def getLastEvent(self, querySet):
		"""if the query has two response, return the latest one"""
		toReturn = querySet[0]

		for val in range(len(querySet)-1):
			if toReturn.timeStamp < val.timeStamp:
				toReturn = val

		return toReturn
