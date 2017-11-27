import os
import django
import logging
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from django.utils import timezone
from django.db import transaction
from AndroidRequests.models import ActiveToken, EventForBusStop, EventForBusv2, TranSappUser, ScoreHistory, Token
from AndroidRequests.scoreFunctions import check_complete_trip_score

# for cleanActiveTokenTable method
MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS = 10

# for clearEventsThatHaveBeenDecline method
MINIMUM_NUMBER_OF_DECLINES = 30
PERCENTAGE_OF_DECLINE_OVER_CONFIRM = 60.0

# time windows to find score history records, if it exists
MINUTE_DELTA = 2


def cleanActiveTokenTable():
    """It cleans the active tokens table on the DB. This checks that the last time a
    token was granted with new position doesn't exceed a big amount of time."""
    logger = logging.getLogger(__name__)

    current_time_minus_x_minutes = timezone.now() - timezone.timedelta(minutes=MINUTES_BEFORE_CLEAN_ACTIVE_TOKENS)
    with transaction.atomic():
        active_tokens = ActiveToken.objects.select_related("token").\
            filter(timeStamp__lt=current_time_minus_x_minutes).all()
        for active_token in active_tokens:
            # check if points are valid
            check_complete_trip_score(active_token.token.token)
            active_token.token.purgeCause = Token.SERVER_DOES_NOT_RECEIVE_LOCATIONS
            active_token.token.save()
            active_token.delete()
            logger.info("{} deleted by clenaActiveTokenTable method".format(active_token.token.token))


def clearEventsThatHaveBeenDecline():
    """This clears the events that have lost credibility"""
    percentage_over_confirm = 1 + PERCENTAGE_OF_DECLINE_OVER_CONFIRM / 100.0

    timestamp = timezone.now()

    # Events for bus stop
    events = EventForBusStop.objects.filter(
        event__eventType='busStop', broken=False,
        expireTime__gte=timestamp, timeCreation__lte=timestamp).order_by('-timeStamp')

    for event in events:
        if event.eventDecline > MINIMUM_NUMBER_OF_DECLINES and \
                                event.eventConfirm * percentage_over_confirm < event.eventDecline:
            event.broken = True
            event.brokenType = EventForBusStop.PERCENTAGE_BETWEEN_POSITIVE_AND_NEGATIVE
            event.save()

    # Event for buses
    events = EventForBusv2.objects.filter(event__eventType='bus', broken=False,
                                          expireTime__gte=timestamp, timeCreation__lte=timestamp).order_by('-timeStamp')

    for event in events:
        if event.eventDecline > MINIMUM_NUMBER_OF_DECLINES and \
                                event.eventConfirm * percentage_over_confirm < event.eventDecline:
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
            previous_score = None
            position = 0
            for user in users:
                if previous_score is None or user.globalScore < previous_score:
                    position += 1
                    previous_score = user.globalScore
                user.globalPosition = position
                user.save()
                print("new position:", user.globalScore, user.globalPosition)
        else:
            print(timezone.now(), "there is not events in last 2 minutes")
