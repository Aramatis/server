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

class SendPoses(View):
	"""This class receives a segment of the trajectory associated to a token."""
	def __init__(self):
		self.context={}

	def get(self, request, pToken, pTrajectory):
		response = {}

		if ActiveToken.objects.filter(token=pToken).exists():
			trajectory = json.loads(pTrajectory)
			trajectory = trajectory['poses']

			#update the token time stamp, for maintanence purpuses
			aToken = ActiveToken.objects.get(token=pToken)
			aToken.timeStamp = timezone.now()
			aToken.save()

			theToken = Token.objects.get(token=pToken)

			for pose in trajectory:
				# set awareness to time stamp, to the server UTC
				aTimeStamp = dateparse.parse_datetime(pose['timeStamp'])

				aTimeStamp = timezone.make_aware(aTimeStamp)

				PoseInTrajectoryOfToken.objects.create(longitud=pose['longitud'],latitud=pose['latitud'],\
					 timeStamp=aTimeStamp, inVehicleOrNot=pose["inVehicleOrNot"],token=theToken)

			response['response'] = 'Poses were register.'
		else:#if the token was not found alert
			response['response'] = 'Token doesn\'t exist.'

		return JsonResponse(response, safe=False)