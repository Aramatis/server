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

from EventsByBus import EventsByBus

class RegisterEventBus(View):
	'''This class handles requests that report events of a bus.'''

	'''Falta agregar la pose a esto'''
	def get(self, request, pUserId, pBusService, pBusPlate, pEventID, pConfirmDecline, pLatitud=500, pLongitud=500):
		response = {}

		# here we request all the info needed to proceed
		aTimeStamp = timezone.now()
		theEvent = Event.objects.get(id=pEventID)
		theBus = Bus.objects.get_or_create(service=pBusService, registrationPlate=pBusPlate)[0]

		# estimate the oldest time where the reported event can be usefull
		# if there is no event here a new one is created
		oldestAlertedTime = aTimeStamp - timezone.timedelta(minutes=theEvent.lifespam)

		# check if there is an event
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

			eventReport.save()

			StadisticDataFromRegistrationBus.objects.create(timeStamp=aTimeStamp, confirmDecline=pConfirmDecline,\
			 reportOfEvent=eventReport, longitud=pLatitud, latitud=pLongitud, userId=pUserId)
		else:
			# if an event was not found, create a new one
			aEventReport = EventForBus.objects.create(userId=pUserId, bus=theBus, event=theEvent, timeStamp=aTimeStamp,\
                                timeCreation=aTimeStamp)

			# set the initial values for this fields
			if pConfirmDecline == 'decline':
				aEventReport.eventDecline = 1
				aEventReport.eventConfirm = 0

			aEventReport.save()

			StadisticDataFromRegistrationBus.objects.create(timeStamp=aTimeStamp, confirmDecline=pConfirmDecline, \
				reportOfEvent=aEventReport, longitud=pLatitud, latitud=pLongitud, userId=pUserId)

                """ Returns updated event list for a bus """
                eventsByBus = EventsByBus()
                return eventsByBus.get(request, pBusPlate, pBusService)
		# response['response'] = 'Thanks for the information, give to receive.'
		# return JsonResponse(response, safe=False)

	def getLastEvent(self, querySet):
		"""if the query has two responses, return the latest one"""
		toReturn = querySet[0]

		for val in range(len(querySet)-1):
			if toReturn.timeStamp < val.timeStamp:
				toReturn = val

		return toReturn
