import os, sys
from Loaders.LoaderFactory import LoaderFactory
from Loaders.ModelLoaders import LoadEvents
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()


from AndroidRequests.models import *
from django.utils import timezone

def cleanActiveTokenTable():
	"""It cleans the active tokens table on the DB. This checks that the last time a 
	token was granted with new position doesn't exceed a big amount of time."""

	activeTokens = ActiveToken.objects.all()
	currentTimeMinus11Minutes = timezone.now() - timezone.timedelta(minutes=30)
	for aToken in activeTokens:
		if aToken.timeStamp < currentTimeMinus11Minutes:
			aToken.delete()

def clearnEventsThatHaveBeenDecline():
	'''This clears the events that have lost credibility'''
	minimumNumberOfDeclines = 30
	porcentageOfDeclineOverConfirm = 60.0 

	currentEventReport = []

	events = Event.objects.filter(eventType='busStop')

	for event in events:
		eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)
		aux = EventForBusStop.objects.filter(event=event,timeStamp__gt=eventTime).order_by('-timeStamp')

		
		for evnt in aux:
			currentEventReport.append(evnt)

	for event in currentEventReport:

		if event.eventDecline > minimumNumberOfDeclines:
			if event.eventConfirm*(1 + porcentageOfDeclineOverConfirm /100.0 ) < event.eventDecline:
				theEvent = event.event
				event.timeStamp = event.timeCreation - timezone.timedelta(minutes=theEvent.lifespam + 10)
				event.save()



	eventsToAsk = Event.objects.filter(eventType='bus')

	currentEventReport = []


	for event in eventsToAsk:
		eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)

		registry = EventForBus.objects.filter( event=event,timeStamp__gt=eventTime).order_by('-timeStamp')

		for aux in registry:
			currentEventReport.append(aux)

	for event in currentEventReport:

		if event.eventDecline > minimumNumberOfDeclines:
			if event.eventConfirm * (1 + porcentageOfDeclineOverConfirm /100.0) < event.eventDecline:
				theEvent = event.event
				event.timeStamp = event.timeCreation - timezone.timedelta(minutes=theEvent.lifespam + 10)
				event.save()