from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone
from django.forms import model_to_dict

#python utilities
import requests, json
import datetime
# my stuff
# import DB's models
from AndroidRequests.models import *

class EventsByBus(View):
	"""This class handles request for the registered event for an specific bus."""
	def __init__(self):
		self.context={}

	def get(self, request, pRegistrationPlate,pBusService):
		"""It is important to give the registrarion plate and the bus
		service, becuase one plate could gave two service."""
		response = {}
		bus = Bus.objects.get(registrationPlate=pRegistrationPlate, service=pBusService)
		response['registrationPlate'] = pRegistrationPlate
		response['service'] = bus.service

		# ask for the events in this bus
		events = self.getEventForBus(bus)

		response['events'] = events

		return JsonResponse(response, safe=False)

	def getEventForBus(self,pBus):
		"""this method look for the active envents of a bus, thouse whoms lifespam hasn't expire since the
		last time there where reported"""
		events = []

		for event in pBus.events.all():
			registry = EventForBus.objects.filter(bus = pBus, event=event).order_by('-timeStamp')[0]

			#checks if the event is active
			if(registry.timeStamp + datetime.timedelta(minutes = event.lifespam)<timezone.now()):
				continue

			# ask the specific data for the event. It's a dictionary defied in the models
			registryDict = registry.getDictionary()
			# this makes a list of dictionarys
			events.append(registryDict)
			
		return events