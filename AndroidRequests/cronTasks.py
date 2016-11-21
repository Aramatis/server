import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from AndroidRequests.models import ActiveToken, Event, EventForBusStop, EventForBusv2
from django.utils import timezone

import logging

# for cleanActiveTokenTable method
MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS = 10

# for clearEventsThatHaveBeenDecline method
MINIMUM_NUMBER_OF_DECLINES = 30
PORCENTAGE_OF_DECLINE_OVER_CONFIRM = 60.0

def cleanActiveTokenTable():
    """It cleans the active tokens table on the DB. This checks that the last time a
    token was granted with new position doesn't exceed a big amount of time."""
    logger = logging.getLogger(__name__)

    activeTokens = ActiveToken.objects.all()
    currentTimeMinusXMinutes = timezone.now() - timezone.timedelta(minutes=MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS)
    for aToken in activeTokens:
        if aToken.timeStamp < currentTimeMinusXMinutes:
            aToken.delete()
            logger.info("{} deleted by clenaActiveTokenTable method".format(aToken.token.token))

def clearEventsThatHaveBeenDecline():
    '''This clears the events that have lost credibility'''
    percentageOverConfirm = 1 + PORCENTAGE_OF_DECLINE_OVER_CONFIRM /100.0

    # Events for bus stop
    events = Event.objects.filter(eventType='busStop')
    currentEventReport = []

    for event in events:
        eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)
        aux = EventForBusStop.objects.\
                filter(event=event,timeStamp__gt=eventTime)\
                .order_by('-timeStamp')

        for evnt in aux:
            currentEventReport.append(evnt)

        for event in currentEventReport:
            if event.eventDecline > MINIMUM_NUMBER_OF_DECLINES and \
               event.eventConfirm * percentageOverConfirm < event.eventDecline:
                theEvent = event.event
                event.timeStamp = event.timeCreation - \
                        timezone.timedelta(minutes=theEvent.lifespam + 10)
                event.save()

    # Event for buses
    eventsToAsk = Event.objects.filter(eventType='bus')
    currentEventReport = []

    for event in eventsToAsk:
        eventTime = timezone.now() - timezone.timedelta(minutes=event.lifespam)
        registry = EventForBusv2.objects.\
                filter(event=event, timeStamp__gt=eventTime).\
                order_by('-timeStamp')

        for aux in registry:
            currentEventReport.append(aux)

        for event in currentEventReport:
            if event.eventDecline > MINIMUM_NUMBER_OF_DECLINES and \
               event.eventConfirm * percentageOverConfirm < event.eventDecline:
                theEvent = event.event
                event.timeStamp = event.timeCreation - \
                        timezone.timedelta(minutes=theEvent.lifespam + 10)
                event.save()
