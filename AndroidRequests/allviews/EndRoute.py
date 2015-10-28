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

class EndRoute(View):
	"""This class handles the ending of a trip tracking removing the token
	from the active token table."""
	def __init__(self):
		self.context={}

	def get(self, request, pToken):
		
		response = {}

		if ActiveToken.objects.filter(token=pToken).exists():
			aToken = ActiveToken.objects.get(token=pToken).delete()
			response['response'] = 'Trip ended.'
		else:#if the token was not found alert
			response['response'] = 'Token doesn\'t exist.'

		return JsonResponse(response, safe=False)