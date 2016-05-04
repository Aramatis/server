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

class RequestToken(View):
	"""This class handles the start of the tracking, assigning a token
	to identify the trip, not the device."""

	def __init__(self):
		self.context={}

	def get(self, request, pUserId, pBusService, pRegistrationPlate):
		data = timezone.now() # the token is primary a hash of the
		salt = os.urandom(20) # time stamp plus a random salt
		hashToken = hashlib.sha512( str(data) + salt ).hexdigest()
		bus = Bus.objects.get_or_create(registrationPlate = pRegistrationPlate, \
		 service = pBusService)[0]

		aToken = Token.objects.create(userId=pUserId, token=hashToken, bus=bus, \
                        color=self.getRandomColor())
		ActiveToken.objects.create(timeStamp=data,token=aToken)

		# we store the active token
		response = {}
		response['token'] = hashToken

		return JsonResponse(response, safe=False)

	def getRandomColor(self):
		letters = '0123456789ABCDEF0'
		color = '#'
		colors = {'#2c7fb8','#dd1c77','#016c59','#de2d26','#d95f0e'}
		color = list(colors)[int(round(random() * 4))]
		return color
