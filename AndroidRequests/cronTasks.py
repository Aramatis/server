import os
import django
import logging
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from django.utils import timezone
from django.db import transaction
from AndroidRequests.models import ActiveToken, EventForBusStop, EventForBusv2, TranSappUser, ScoreHistory
from AndroidRequests.scoreFunctions import checkCompleteTripScore

# for cleanActiveTokenTable method
MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS = 10

# for clearEventsThatHaveBeenDecline method
MINIMUM_NUMBER_OF_DECLINES = 30
PORCENTAGE_OF_DECLINE_OVER_CONFIRM = 60.0

# time windows to find score history records, if it exists
MINUTE_DELTA = 2


def cleanActiveTokenTable():
    """It cleans the active tokens table on the DB. This checks that the last time a
    token was granted with new position doesn't exceed a big amount of time."""
    logger = logging.getLogger(__name__)

    currentTimeMinusXMinutes = timezone.now() - timezone.timedelta(minutes=MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS)
    activeTokens = ActiveToken.objects.select_related("token").filter(timeStamp__lt=currentTimeMinusXMinutes).all()
    for activeToken in activeTokens:
        # check if points are valid
        checkCompleteTripScore(activeToken.token.token)
        activeToken.delete()
        logger.info("{} deleted by clenaActiveTokenTable method".format(activeToken.token.token))


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

def updateGlobalRanking():
    """ update ranking position for TranSapp users """
    with transaction.atomic():
        delta = timezone.now() - datetime.timedelta(minutes=MINUTE_DELTA)

        if ScoreHistory.objects.filter(timeCreation__gt=delta).count() > 0:
            print(timezone.now(), "updating global ranking")
            users = TranSappUser.objects.select_related('level').order_by('-globalScore')
            previousScore = None
            position = 0
            for user in users:
                if previousScore is None or user.globalScore < previousScore:
                    position += 1
                    previousScore = user.globalScore
                user.globalPosition = position
                user.save()
                print("new position:", user.globalScore, user.globalPosition)
        else:
            print(timezone.now(), "there is not events in last 2 minutes")