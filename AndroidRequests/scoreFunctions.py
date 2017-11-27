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

    def validate_user(self, user_id, session_token):
        """ validate user session """
        response = {}
        user_is_logged = False
        transapp_user = None

        if user_id and session_token:
            try:
                user = TranSappUser.objects.select_related('level').get(userId=user_id)

                if user.sessionToken == uuid.UUID(session_token):
                    user_is_logged = True
                    transapp_user = user
                    Status.getJsonStatus(Status.OK, response)
                else:
                    Status.getJsonStatus(Status.INVALID_SESSION_TOKEN, response)
            except TranSappUser.DoesNotExist:
                Status.getJsonStatus(Status.INVALID_USER, response)
        else:
            Status.getJsonStatus(Status.INVALID_PARAMS, response)

        return user_is_logged, transapp_user, response


class CalculateScore:
    """ Abstract class  """
    __metaclass__ = abc.ABCMeta

    def __init__(self, request):
        """
        @request django.http.request
        """
        self.logger = logging.getLogger(__name__)

        user_id = request.POST.get('userId', None)
        session_token = request.POST.get('sessionToken', None)

        self.user_is_logged, self.user, self.response = UserValidation().validate_user(user_id, session_token)

    @abc.abstractmethod
    def get_score(self, event_id, meta_data):
        return

    def update_score(self, score_event, meta):
        if self.user_is_logged:
            additional_score = self.get_score(score_event, meta)

            self.user.globalScore += additional_score
            self.user.save()

            if self.user.globalScore > self.user.level.maxScore:
                next_level = Level.objects.get(position=self.user.level.position + 1)
                self.user.level = next_level
                self.user.save()

            if meta is not None:
                meta = json.dumps(meta, cls=TranSappJSONEncoder)
            # to score log
            score_event_obj = ScoreEvent.objects.get(code=score_event)
            ScoreHistory.objects.create(tranSappUser=self.user, scoreEvent=score_event_obj,
                                        timeCreation=timezone.now(), score=additional_score, meta=meta)

            self.response['userData'] = self.user.get_score_data()

        return self.response


class EventScore(CalculateScore):
    """ update score based on bus event or bus stop event """

    def __init__(self, request):
        CalculateScore.__init__(self, request)

    def get_score(self, event_id, meta_data):
        """ It calculates score """
        try:
            score = ScoreEvent.objects.get(code=event_id).score
        except ScoreEvent.DoesNotExist:
            error_msg = 'event code: {} does not exist in database'.format(event_id)
            self.logger.error(error_msg)
            score = 0

        return score


class DistanceScore(CalculateScore):
    """ update score based on distance on the bus """

    def __init__(self, request):
        CalculateScore.__init__(self, request)

    def get_score(self, event_id, meta):
        """ It calculates score """

        points = meta['poses']
        token = meta['token']

        distance = 0
        timestamp = points[0][2]
        previous_point = PoseInTrajectoryOfToken.objects.filter(token__token=token, timeStamp__lt=timestamp).\
            order_by('-timeStamp').first()
        if previous_point is not None:
            distance += gpsFunctions.haversine(previous_point.longitude, previous_point.latitude,
                                               points[0][0], points[0][1], measure='km')

        try:
            score = ScoreEvent.objects.get(code=event_id).score
        except ScoreEvent.DoesNotExist:
            error_msg = 'event code: {} does not exist in database'.format(event_id)
            self.logger.error(error_msg)
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


def check_complete_trip_score(trip_token):
    """
    Update score based on all data of a trip. Conditions:
    1 - total distances greater than 100 meters
    2 - total time is greater than 1 minute
    """
    old_score = 0
    evaluation_event = "evn00301"
    score_history_objs = list(
        ScoreHistory.objects.filter(meta__contains=trip_token, tranSappUser__isnull=False).exclude(
            scoreEvent__code=evaluation_event).order_by("timeCreation"))

    if len(score_history_objs) > 0:
        # search first location
        first_point = None
        last_point = None

        for score_history_obj in score_history_objs:
            old_score += score_history_obj.score
            locations = json.loads(score_history_obj.meta)["poses"]
            if len(locations) > 0:
                if first_point is None:
                    first_point = locations[0]
                last_point = locations[-1]
        old_score = round(old_score, 8)

        if first_point is not None and last_point is not None:
            start_time = dateparse.parse_datetime(first_point[2])
            last_time = dateparse.parse_datetime(last_point[2])

            distance = gpsFunctions.haversine(first_point[0], first_point[1], last_point[0], last_point[1])
            diff_time = (last_time - start_time).total_seconds()

            # if distance is less than 100 meters or duration is less than 1 minute, subtract points
            second_limit = 1 * 60
            distance_limit_mts = 100

            if distance < distance_limit_mts or diff_time < second_limit:
                new_score = 0
                ScoreHistory.objects.filter(meta__contains=trip_token, tranSappUser__isnull=False). \
                    exclude(scoreEvent__code=evaluation_event).update(score=new_score)

                # if user evaluate trip we don't give point for that
                evaluation_event = "evn00301"
                try:
                    evaluation_obj = ScoreHistory.objects.get(meta__contains=trip_token,
                                                              scoreEvent__code=evaluation_event)
                    old_score += evaluation_obj.score
                    evaluation_obj.score = 0
                    evaluation_obj.save()
                except ScoreHistory.DoesNotExist:
                    pass

                user = TranSappUser.objects.select_related("level").get(id=score_history_objs[0].tranSappUser_id)
                user.globalScore -= old_score
                if user.globalScore < user.level.minScore:
                    user.level = Level.objects.get(position=user.level.position - 1)
                user.save()


def calculate_event_score(request, event_id, meta_data=None):
    """ """
    ces = EventScore(request)
    return ces.update_score(event_id, meta_data)


def calculate_distance_score(request, event_id, meta_data):
    """ """
    ces = DistanceScore(request)
    return ces.update_score(event_id, meta_data)
