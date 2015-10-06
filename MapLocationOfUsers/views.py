# usefull packages from django
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.utils import timezone


# models 
from AndroidRequests.models import DevicePositionInTime

# Create your views here.

class MapHandler(View):
	'''This class manages the map where the markers from the devices using the
	aplication are shown'''
	
	def __init__(self):
		"""the contructor, context are the parameter given to the html template"""
		self.context={}	

	def get(self, request):
		template = "googelMap.html"

		return render(request, template, self.context)

class GetMapPositions(View):
	'''This class request to to the database the values of the actives users'''
	
	def __init__(self):
		"""the contructor, context are the parameter given to the html template"""
		self.context={}	

	def get(self, request):
		template = "googelMap.html"

		now = timezone.now()
		earlier = now - timezone.timedelta(minutes=10)

		# the position of intereset are the ones ocurred in the lat 10 minutes
		postions = DevicePositionInTime.objects.filter(timeStamp__range=(earlier,now))

		response = []
		for aPosition in postions:
			response.append({'latitud': aPosition.latitud, 'longitud': aPosition.longitud})

		return JsonResponse(response, safe=False)