# -*- coding: utf-8 -*-
from django.utils import timezone, dateparse

from AndroidRequests.models import TranSappUser, ScoreHistory, ScoreEvent, Level, PoseInTrajectoryOfToken
from AndroidRequests.statusResponse import Status
from AndroidRequests.encoder import TranSappJSONEncoder

import AndroidRequests.gpsFunctions as gpsFunctions
import abc
import logging
import uuid
import json


class UserValidation(object):
    """ it validates  user session """

    def __init__(self):
        pass

    def validateUser(self, userId, sessionToken):
        """ validate user session """
        response = {}
        userIsLogged = False
        tranSappUser = None

        if userId and sessionToken:
            try:
                user = TranSappUser.objects.select_related('level'). \
                    get(userId=userId)

                if user.sessionToken == uuid.UUID(sessionToken):
                    userIsLogged = True
                    tranSappUser = user
                    Status.getJsonStatus(Status.OK, response)
                else:
                    Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, response)
            except TranSappUser.DoesNotExist:
                Status.getJsonStatus(Status.INVALID_USER, response)
        else:
            Status.getJsonStatus(Status.INVALID_PARAMS, response)

        return userIsLogged, tranSappUser, response


class CalculateScore:
    """ Abstract class  """
    __metaclass__ = abc.ABCMeta

    def __init__(self, request):
        """
        @request django.http.request
        """
        self.logger = logging.getLogger(__name__)

        userId = request.POST.get('userId', None)
        sessionToken = request.POST.get('sessionToken', None)

        self.userIsLogged, self.user, self.response = UserValidation().validateUser(userId, sessionToken)

    @abc.abstractmethod
    def getScore(self, eventCode, metaData):
        return

    def updateScore(self, scoreEvent, meta):
        if self.userIsLogged:
            additionalScore = self.getScore(scoreEvent, meta)

            self.user.globalScore += additionalScore
            self.user.save()

            if self.user.globalScore > self.user.level.maxScore:
                nextLevel = Level.objects.get(position=self.user.level.position + 1)
                self.user.level = nextLevel
                self.user.save()

            if meta is not None:
                meta = json.dumps(meta, cls=TranSappJSONEncoder)
            # to score log
            scoreEventObj = ScoreEvent.objects.get(code=scoreEvent)
            ScoreHistory.objects.create(tranSappUser=self.user, scoreEvent=scoreEventObj,
                                        timeCreation=timezone.now(), score=additionalScore, meta=meta)

            self.response['userData'] = self.user.getScoreData()

        return self.response


class EventScore(CalculateScore):
    """ update score based on bus event or bus stop event """

    def __init__(self, request):
        CalculateScore.__init__(self, request)

    def getScore(self, eventCode, metaData):
        """ It calculates score """
        try:
            score = ScoreEvent.objects.get(code=eventCode).score
        except ScoreEvent.DoesNotExist:
            errorMsg = 'event code: {} does not exist in database'.format(eventCode)
            self.logger.error(errorMsg)
            score = 0

        return score


class DistanceScore(CalculateScore):
    """ update score based on distance on the bus """

    def __init__(self, request):
        CalculateScore.__init__(self, request)

    def getScore(self, eventCode, meta):
        """ It calculates score """

        points = meta['poses']
        token = meta['token']

        distance = 0
        timestamp = points[0][2]
        previousPoint = PoseInTrajectoryOfToken.objects.filter(token__token=token, timeStamp__lt=timestamp).\
            order_by('-timeStamp').first()
        if previousPoint is not None:
            distance += gpsFunctions.haversine(previousPoint.longitude, previousPoint.latitude,
                                               points[0][0], points[0][1], measure='km')

        try:
            score = ScoreEvent.objects.get(code=eventCode).score
        except ScoreEvent.DoesNotExist:
            errorMsg = 'event code: {} does not exist in database'.format(eventCode)
            self.logger.error(errorMsg)
            score = 0

        for index, point in enumerate(points[:-1]):
            longitude = point[0]
            latitude = point[1]
            distance += gpsFunctions.haversine(longitude, latitude,
                                               points[index + 1][0], points[index + 1][1],
                                               measure='km')

        # if distance is higher than 8 kilometers, fake!! don't give a shit
        if distance > 8:
            distance = 0

        return round(score * distance, 8)


def checkCompleteTripScore(trip_token):
    """
    Update score based on all data of a trip. Conditions:
    1 - total distances greater than 100 meters
    2 - total time is greater than 1 minute
    """
    oldScore = 0
    evaluationEvent = "evn00301"
    scoreHistoryObjs = list(ScoreHistory.objects.filter(meta__contains=trip_token, tranSappUser__isnull=False).\
                            exclude(scoreEvent__code=evaluationEvent).order_by("timeCreation"))

    if len(scoreHistoryObjs) > 0:
        #search first location
        firstPoint = None
        lastPoint = None

        for scoreHistoryObj in scoreHistoryObjs:
            oldScore += scoreHistoryObj.score
            locations = json.loads(scoreHistoryObj.meta)["poses"]
            if len(locations) > 0:
                if firstPoint is None:
                    firstPoint = locations[0]
                lastPoint = locations[-1]
        oldScore = round(oldScore, 8)

        if firstPoint is not None and lastPoint is not None:
            startTime = dateparse.parse_datetime(firstPoint[2])
            lastTime = dateparse.parse_datetime(lastPoint[2])

            distance = gpsFunctions.haversine(firstPoint[0], firstPoint[1], lastPoint[0], lastPoint[1])
            diffTime = (lastTime-startTime).total_seconds()

            # if distance is less than 100 meters or duration is less than 1 minute, subtract points
            second_limit = 1 * 60
            distance_limit_mts = 100

            if distance < distance_limit_mts or diffTime < second_limit:
                newScore = 0
                ScoreHistory.objects.filter(meta__contains=trip_token, tranSappUser__isnull=False).\
                    exclude(scoreEvent__code=evaluationEvent).update(score=newScore)

                # if user evaluate trip we don't give point for that
                evaluationEvent = "evn00301"
                try:
                    evaluationObj = ScoreHistory.objects.get(meta__contains=trip_token,
                                                             scoreEvent__code=evaluationEvent)
                    oldScore += evaluationObj.score
                    evaluationObj.score = 0
                    evaluationObj.save()
                except ScoreHistory.DoesNotExist:
                    pass

                user = TranSappUser.objects.select_related("level").get(id=scoreHistoryObjs[0].tranSappUser_id)
                user.globalScore -= oldScore
                if user.globalScore < user.level.minScore:
                    previousLevel = Level.objects.get(position=user.level.position - 1)
                    user.level = previousLevel
                user.save()


def calculateEventScore(request, eventCode, metaData=None):
    """ """
    ces = EventScore(request)
    return ces.updateScore(eventCode, metaData)


def calculateDistanceScore(request, eventCode, metaData):
    """ """
    ces = DistanceScore(request)
    return ces.updateScore(eventCode, metaData)
