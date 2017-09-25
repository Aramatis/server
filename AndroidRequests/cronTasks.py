import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from AndroidRequests.models import ActiveToken, EventForBusStop, EventForBusv2
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
    currentTimeMinusXMinutes = timezone.now(
    ) - timezone.timedelta(minutes=MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS)
    for aToken in activeTokens:
        if aToken.timeStamp < currentTimeMinusXMinutes:
            aToken.delete()
            logger.info(
                "{} deleted by clenaActiveTokenTable method".format(
                    aToken.token.token))


def clearEventsThatHaveBeenDecline():
    """This clears the events that have lost credibility"""
    percentageOverConfirm = 1 + PORCENTAGE_OF_DECLINE_OVER_CONFIRM / 100.0

    timeStamp = timezone.now()

    # Events for bus stop
    events = EventForBusStop.objects.filter(
        event__eventType='busStop', broken=False,
        expireTime__gte=timeStamp, timeCreation__lte=timeStamp).order_by('-timeStamp')

    for event in events:
        if event.eventDecline > MINIMUM_NUMBER_OF_DECLINES and \
                                event.eventConfirm * percentageOverConfirm < event.eventDecline:
            event.broken = True
            event.brokenType = EventForBusStop.PERCENTAGE_BETWEEN_POSITIVE_AND_NEGATIVE
            event.save()

    # Event for buses
    events = EventForBusv2.objects.filter(event__eventType='bus', broken=False,
                                          expireTime__gte=timeStamp, timeCreation__lte=timeStamp).order_by('-timeStamp')

    for event in events:
        if event.eventDecline > MINIMUM_NUMBER_OF_DECLINES and \
                                event.eventConfirm * percentageOverConfirm < event.eventDecline:
            event.broken = True
            event.brokenType = EventForBusv2.PERCENTAGE_BETWEEN_POSITIVE_AND_NEGATIVE
            event.save()
