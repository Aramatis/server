# -*- coding: utf-8 -*-
from django.utils import timezone, dateparse

import abc
import uuid
import logging
import json

import AndroidRequests.gpsFunctions as gpsFunctions

from AndroidRequests.statusResponse import Status
from AndroidRequests.models import TranSappUser, ScoreHistory, ScoreEvent, Level, PoseInTrajectoryOfToken


class CalculateScore():
    """ Abstract class  """
    __metaclass__ = abc.ABCMeta

    def __init__(self, request):
        """
        @request django.http.request
        """
        self.logger = logging.getLogger(__name__)
        self.isUpdatedScore, self.user, self.response = self.validateParams(request)

    def validateParams(self, request):

        userId = request.POST.get('userId', '')
        sessionToken = request.POST.get('sessionToken', '')

        response = {}
        Status.getJsonStatus(Status.OK, response)
        response['userData'] = {}
        response['userData']['score'] = -1
        response['userData']['level'] = {}
        response['userData']['level']['name'] = ''
        response['userData']['level']['maxScore'] = ''

        if userId and sessionToken:
            try:
                user = TranSappUser.objects.get(userId=userId)

                if user.sessionToken == uuid.UUID(sessionToken):
                    return True, user, response
                else:
                    Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, response)
            except TranSappUser.DoesNotExist:
                    Status.getJsonStatus(Status.INVALID_USER, response)
        else:
            Status.getJsonStatus(Status.INVALID_PARAMS, response)

        return False, None, response

    @abc.abstractmethod
    def getScore(self, eventCode, metaData):
        return

    def updateScore(self, scoreEvent, meta=None):
        if self.isUpdatedScore:
            additionalScore = self.getScore(scoreEvent, meta)

            self.user.globalScore += additionalScore
            self.user.save()
            
            if self.user.globalScore > self.user.level.maxScore:
                nextLevel = Level.objects.get(position=self.user.level.position+1)
                self.user.level = nextLevel
                self.user.save()

            # to score log
            scoreEventObj = ScoreEvent.objects.get(code=scoreEvent)
            ScoreHistory.objects.create(tranSappUser=self.user, scoreEvent=scoreEventObj, 
                    timeCreation=timezone.now(), score=additionalScore, meta=meta)
            
            self.response['userData']['score'] = self.user.globalScore
            self.response['userData']['level']['name'] = self.user.level.name
            self.response['userData']['level']['maxScore'] = self.user.level.maxScore

        return self.response
        

class EventScore(CalculateScore):
    """ update score based on bus event or bus stop event """

    def __init__(self, request):
        CalculateScore.__init__(self, request)

    def getScore(self, eventCode, metaData):
        """ It calculates score """
        try:
            score = ScoreEvent.objects.get(code=eventCode).score
        except:
            errorMsg = 'event code: {} does not exist in database'.format(eventCode)
            self.logger.error(errorMsg)
            score = 0

        return score

class DistanceScore(CalculateScore):
    """ update score based on distance on the bus """

    def __init__(self, request):
        CalculateScore.__init__(self, request)

    def getScore(self, eventCode, metaData):
        """ It calculates score """

        points = metaData['poses']
        tripToken = metaData['tripToken']
        
        firstPointTime = dateparse.parse_datetime(points[0]['timeStamp'])
        firstPointTime = timezone.make_aware(firstPointTime)
        distance = 0
        try:
            previousPoint = PoseInTrajectoryOfToken.objects.filter(token__token=tripToken, 
                timeStamp__lt=firstPointTime).order_by('-timeStamp')[0]
            distance += gpsFunctions.haversine(previousPoint.longitud, previousPoint.latitud, 
                points[0]['longitud'], points[0]['latitud'], measure='km')
        except:
            # there is not previous point
            pass

        try:
            score = ScoreEvent.objects.get(code=eventCode).score
        except:
            errorMsg = 'event code: {} does not exist in database'.format(eventCode)
            self.logger.error(errorMsg)
            score = 0

        for index, point in enumerate(points[:-1]):
            distance += gpsFunctions.haversine(point['longitud'], point['latitud'], 
                points[index+1]['longitud'], points[index+1]['latitud'], measure='km')
        
        return round(score * distance, 8)


def calculateEventScore(request, eventCode):
    """ """
    ces = EventScore(request)
    return ces.updateScore(eventCode)

def calculateDistanceScore(request, eventCode, metaData):
    """ """
    ces = DistanceScore(request)
    return ces.updateScore(eventCode, metaData)


