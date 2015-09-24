from django.shortcuts import render
from django.views.generic import View

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