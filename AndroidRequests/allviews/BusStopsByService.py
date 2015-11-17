from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

# import DB's models
from AndroidRequests.models import *
from AndroidRequests.allviews.EventsByBusStop import *

class BusStopsByService(View):
	"""This class handles request for the list of bus stop for an specific service."""
	def __init__(self):
		self.context={}

	def get(self, request, pBusService):
		"""it receive the bus Service to get all the bus stops where it service stops."""
		response = {}
		response['service'] = pBusService

		# ask for the bus stops for this service
		busStops = self.getBusStopsForService(pBusService)

		response['paraderos'] = busStops

		return JsonResponse(response, safe=False)

	def getBusStopsForService(self,pBusService):
		"""this method look for all the bus stops where the service stops."""
		busStops = []		

		for sbs in ServicesByBusStop.objects.filter(service=pBusService):
			data = {}
			busStop = sbs.busStop
			data['codigo'] = busStop.code
			data['nombre'] = busStop.name
			data['latitud'] = busStop.latitud
			data['longitud'] = busStop.longitud
			getEventsByBusStop = EventsByBusStop()
			data['eventos'] = getEventsByBusStop.getEventsForBusStop(busStop, timezone.now())
			busStops.append(data)

		return busStops