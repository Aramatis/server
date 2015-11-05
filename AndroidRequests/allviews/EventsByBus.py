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
		
		response = {}
		bus = Bus.objects.get(registrationPlate=pRegistrationPlate, service=pBusService)
		response['registrationPlate'] = pRegistrationPlate
		response['service'] = bus.service
		events = self.getEventForBus(bus)
		#for event in bus.events.all():
		#	registry = EventForBus.objects.filter(bus = bus, event=event).order_by('-timeStamp')[0]
		#	if(registry.timeStamp + datetime.timedelta(minutes = event.lifespam)<timezone.now()):
		#		continue
		#	eventDict= model_to_dict(event, fields=['name', 'description', 'category'])
		#	registryDict = model_to_dict(registry, fields=['eventConfirm', 'eventDecline', 'aditionalInfo'])
		#	print registryDict
		#	registryDict['confirm'] = registryDict.pop('eventConfirm')
		#	registryDict['decline'] = registryDict.pop('eventDecline')
		#	#registryDict['info'] = registryDict.pop('aditionalInfo')
		#	eventDict.update(registryDict)
		#	events.append(eventDict)

		response['events'] = events

		return JsonResponse(response, safe=False)

	def getEventForBus(self,pBus):
		events = []

		for event in pBus.events.all():
			registry = EventForBus.objects.filter(bus = pBus, event=event).order_by('-timeStamp')[0]

			print registry.timeStamp + datetime.timedelta(minutes = event.lifespam)
			print timezone.now()
			print registry.timeStamp + datetime.timedelta(minutes = event.lifespam)<timezone.now()
			if(registry.timeStamp + datetime.timedelta(minutes = event.lifespam)<timezone.now()):
				continue
			#eventDict= model_to_dict(event, fields=['name', 'description', 'category'])
			#registryDict = model_to_dict(registry, fields=['eventConfirm', 'eventDecline'])
			#registryDict['confirm'] = registryDict.pop('eventConfirm')
			registryDict = registry.getDictionary()#['decline'] = registryDict.pop('eventDecline')
			events.append(registryDict)
			
		return events