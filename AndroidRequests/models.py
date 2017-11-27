from django.conf import settings
from django.db import models
from django.utils import timezone

from gtfs.models import Location, BusStop, Service, ServiceLocation, ServicesByBusStop, ServiceStopDistance
from gpsFunctions import haversine

import logging
import uuid


class DevicePositionInTime(Location):
    """Helps storing the position of active users"""
    timeStamp = models.DateTimeField("Time Stamp", null=False, blank=False)
    """ Specific date time when the server received the device's position """
    phoneId = models.UUIDField()
    """ To identify the data owner """


class Event(models.Model):
    """Here are all the events, it's configuration and information."""
    id = models.CharField('Identifier', max_length=8, primary_key=True)
    """ string code that identifies the event """
    name = models.CharField('Name', max_length=30, null=False, blank=False)
    """ It's a short name for the event """
    description = models.CharField('Description', max_length=140, null=True)
    """ Explain the event with a better detail level """
    lifespam = models.IntegerField(
        'Lifespan', default=30)  # this value is in minutes
    """ It represents the time (in minutes) during which the event is valid since the last report """
    category = models.CharField('Category', max_length=20)
    """ group of events with a similar context """

    REPORT_ORIGIN = (
        ('i', 'the event was taken inside the bus'),  # this is an I for inside
        ('o', 'the event was taken from a bustop'),)  # this is an O for outside
    BUS_TYPE = 'bus'
    STOP_TYPE = 'busStop'
    REPORT_TYPE = (
        (BUS_TYPE, 'An event for the bus.'),
        (STOP_TYPE, 'An event for the busStop.'))
    origin = models.CharField(
        'Origin',
        max_length=1,
        choices=REPORT_ORIGIN,
        default='o')
    """ Represents the place from where the event was reported """
    eventType = models.CharField(
        'Event Type',
        max_length=7,
        choices=REPORT_TYPE)
    """ Represents the element to which the event refers """

    def getDictionary(self):
        """ Return a dictionary with the event information """
        dictionary = {'name': self.name, 'description': self.description, 'eventcode': self.id}
        return dictionary


##
#
# These are the models to handle the event registration for a bus or a bus stop
#
##


class StadisticDataFromRegistration(Location):
    timeStamp = models.DateTimeField('Time Stamp', null=False, blank=False)
    """ Specific date time when the server received the event registration """
    confirmDecline = models.CharField('Confirm - Decline', max_length=10)
    """ Represents if the event was confirmed or declined """
    phoneId = models.UUIDField()
    """ To identify the data owner """
    tranSappUser = models.ForeignKey('TranSappUser', null=True)
    """ logged user in app that made the report """

    class Meta:
        abstract = True

    def getDictionary(self):
        """ return two list: one with confirm users and another with decline users """
        dictionary = {}
        if self.tranSappUser is not None:
            dictionary['user'] = self.tranSappUser.getDictionary()
        else:
            dictionary['user'] = {}
        dictionary['vote'] = self.confirmDecline
        timeStamp = timezone.localtime(self.timeStamp)
        dictionary['timeStamp'] = timeStamp.strftime("%d-%m-%Y %H:%M:%S")

        return dictionary


class StadisticDataFromRegistrationBus(StadisticDataFromRegistration):
    """ Save the report done for a user to confirm or decline a bus event """
    reportOfEvent = models.ForeignKey(
        'EventForBusv2', verbose_name='Bus Event')

    gpsLongitude = models.FloatField('GPS Longitude', null=True, blank=False)
    """ longitude of the bus GPS """
    gpsLatitude = models.FloatField('GPS Latitude', null=True, blank=False)
    """ latitude of the bus GPS """
    gpsTimeStamp = models.DateTimeField(
        'GPS Time Stamp', null=True, blank=False)
    """ date time of the bus GPS position data """
    distance = models.FloatField('Distance', null=True, blank=False)
    """ distance from the report to the bus GPS """


class StadisticDataFromRegistrationBusStop(StadisticDataFromRegistration):
    """ Save the report done for a user to confirm or decline a bus stop event """
    reportOfEvent = models.ForeignKey('EventForBusStop',
                                      verbose_name='Bus Stop Event')


class EventRegistration(models.Model):
    """This model stores the reports of events coming from the passagers of the system of public transport buses."""
    CONFIRM = "confirm"
    DECLINE = "decline"
    timeStamp = models.DateTimeField('Time Stamp')  # lastime it was updated
    """ Specific date time when the server received the event registration """
    timeCreation = models.DateTimeField('Creation Time')
    """ Specific date time when the server received for the first time the event registration """
    expireTime = models.DateTimeField(null=True)
    """ Specific date time when event expired """
    event = models.ForeignKey(Event, verbose_name='The event information')
    eventConfirm = models.IntegerField('Confirmations', default=1)
    """ Amount of confirmations for this event """
    eventDecline = models.IntegerField('Declines', default=0)
    """ amount of declinations for this event """
    phoneId = models.UUIDField()
    """ To identify the data owner """
    broken = models.BooleanField(default=False)
    """ to indecate that event expired by some brokenType """
    # list  of criterion of broken type
    PERCENTAGE_BETWEEN_POSITIVE_AND_NEGATIVE = 'percentage'
    brokenType = models.CharField(max_length=50, default=None, null=True)
    """ indicate why event is broken """

    class Meta:
        abstract = True

    def getDictionary(self):
        """A dictionary with the event information, just what was of interest to return to the app."""
        dictionary = {'eventConfirm': self.eventConfirm, 'eventDecline': self.eventDecline}

        creation = timezone.localtime(self.timeCreation)
        stamp = timezone.localtime(self.timeStamp)
        dictionary['timeCreation'] = creation.strftime("%d-%m-%Y %H:%M:%S")
        dictionary['timeStamp'] = stamp.strftime("%d-%m-%Y %H:%M:%S")

        eventDictionay = self.event.getDictionary()
        dictionary.update(eventDictionay)

        return dictionary

    def createUserLists(self, records):
        """
        create confirmed user list, declined user list and identify user creator (if exists)
        return creatorIndex, confirmedUserList, declinedUserList
        """
        creatorId = None
        creatorIndex = -1

        first = True
        confirmedUserDict = {}
        declinedUserDict = {}
        for record in records.order_by("timeStamp"):
            record = record.getDictionary()
            user = record['user']

            if first and bool(user):
                creatorId = user["id"]
            first = False
            if not bool(user):
                continue

            userId = user["id"]
            if record['vote'] == self.CONFIRM:
                if userId in confirmedUserDict:
                    confirmedUserDict[userId]["votes"] += 1
                else:
                    confirmedUserDict[userId] = user
                    confirmedUserDict[userId]["votes"] = 1
                confirmedUserDict[userId]["lastReportTimestamp"] = record["timeStamp"]

            if record['vote'] == self.DECLINE:
                if userId in declinedUserDict:
                    declinedUserDict[userId]["votes"] += 1
                else:
                    declinedUserDict[userId] = user
                    declinedUserDict[userId]["votes"] = 1
                declinedUserDict[userId]["lastReportTimestamp"] = record["timeStamp"]

        confirmedVoteList = []
        declinedVoteList = []

        for index, (_, user) in enumerate(confirmedUserDict.items()):
            if user["id"] == creatorId:
                creatorIndex = index
            confirmedVoteList.append(user)

        for _, user in declinedUserDict.items():
            declinedVoteList.append(user)

        return creatorIndex, confirmedVoteList, declinedVoteList


class EventForBusStop(EventRegistration):
    """This model stores the reported events for the busStop"""
    stopCode = models.CharField(max_length=6, db_index=True, verbose_name='Stop Code')
    """Indicates the bus stop to which the event refers"""
    aditionalInfo = models.CharField(
        'Additional Information',
        max_length=140,
        default='nothing')
    """ Saves additional information required by the event """

    def getDictionary(self):
        dictionary = super(EventForBusStop, self).getDictionary()

        records = self.stadisticdatafromregistrationbusstop_set.all()
        creatorIndex, confirmedVoteList, declinedVoteList = self.createUserLists(records)

        dictionary['confirmedVoteList'] = confirmedVoteList
        dictionary['declinedVoteList'] = declinedVoteList
        dictionary['creatorIndex'] = creatorIndex

        return dictionary


class EventForBusv2(EventRegistration):
    """This model stores the reported events for the Bus"""
    busassignment = models.ForeignKey('Busassignment', verbose_name='the bus')
    """Indicates the bus to which the event refers"""

    def getDictionary(self):
        dictionary = super(EventForBusv2, self).getDictionary()

        records = self.stadisticdatafromregistrationbus_set.all()
        creatorIndex, confirmedVoteList, declinedVoteList = self.createUserLists(records)

        dictionary['confirmedVoteList'] = confirmedVoteList
        dictionary['declinedVoteList'] = declinedVoteList
        dictionary['creatorIndex'] = creatorIndex

        return dictionary


class ServiceNotFoundException(Exception):
    """ error produced when service information does not exist in service table """


class ServiceDistanceNotFoundException(Exception):
    """ error produced when it is not possible to get distance between a service and bus stop """


class Busv2(models.Model):
    """Represent a bus like the unique combination of registration plate and service as one.
    So there can be two buses with the same service and two buses with the same registration plate.
    The last thing means that one fisical bus can work in two different services."""
    registrationPlate = models.CharField(max_length=8)
    """ It's the registration plate for the bus, without hyphen """
    # service = models.CharField(max_length=5, null=False, blank=False)
    # """ It indicates the service performed by the bus """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    """ Unique ID to primarily identify Buses created without registrationPlate """
    # events = models.ManyToManyField(Event,  verbose_name='the event' ,through=EventForBus)


class Busassignment(models.Model):
    """Represent a bus like the unique combination of registration plate and service as one.
    So there can be two buses with the same service and two buses with the same registration plate.
    The last thing means that one fisical bus can work in two different services."""
    # registrationPlate = models.CharField(max_length=8)
    """ It's the registration plate for the bus, without hyphen """
    service = models.CharField(max_length=11, null=False, blank=False)
    """ It indicates the service performed by the bus """
    uuid = models.ForeignKey(Busv2, verbose_name='Thebusv2')
    """ Unique ID to primarily identify Buses created without registrationPlate """
    events = models.ManyToManyField(
        Event,
        verbose_name='the event',
        through=EventForBusv2)

    class Meta:
        unique_together = ('uuid', 'service')

    def getDirection(self, stopObj, pDistance):
        """ Given a bus stop and the distance from the bus to the bus stop,
            return the address to which point the bus """
        try:
            serviceCode = ServicesByBusStop.objects.filter(
                busStop=stopObj,
                service__service=self.service,
                gtfs__version=settings.GTFS_VERSION).values_list('code', flat=True)[0]
        except ServicesByBusStop.DoesNotExist:
            raise ServiceNotFoundException(
                "Service {} is not present in bus stop {}".format(
                    self.service, stopObj.code))

        try:
            serviceDistance = ServiceStopDistance.objects.filter(
                busStop=stopObj,
                service=serviceCode,
                gtfs__version=settings.GTFS_VERSION).values_list('distance', flat=True)[0]
        except ServiceStopDistance.DoesNotExist:
            raise ServiceDistanceNotFoundException(
                "The distance is not possible getting for bus stop '{}' and service '{}'".format(
                    stopObj.code, serviceCode))

        distance = serviceDistance - int(pDistance)
        # bus service distance from route origin
        greaters = ServiceLocation.objects.filter(
            service=serviceCode,
            gtfs__version=settings.GTFS_VERSION,
            distance__gt=distance).order_by('distance')[:1]
        # get 2 locations greater than current location (nearer to the bus
        # stop)
        lowers = ServiceLocation.objects.filter(
            service=serviceCode,
            gtfs__version=settings.GTFS_VERSION,
            distance__lte=distance).order_by('-distance')[:1]
        # get 2 locations lower than current location

        # we need two point to detect the bus direction (left, right, up, down)
        if len(greaters) > 0 and len(lowers) > 0:
            greater = greaters[0]
            lower = lowers[0]
        elif len(greaters) == 0 and len(lowers) == 2:
            greater = lowers[0]
            lower = lowers[1]
        elif len(greaters) == 0 and len(lowers) == 1:
            greater = lowers[0]
            lower = lowers[0]
        elif len(lowers) == 0 and len(greaters) == 2:
            lower = greaters[0]
            greater = greaters[1]
        elif len(lowers) == 0 and len(greaters) == 1:
            lower = greaters[0]
            greater = greaters[0]
        elif len(lowers) == 0 and len(greaters) == 2:
            lower = greaters[0]
            greater = greaters[1]
        elif len(greaters) == 0 and len(lowers) == 0:
            # there are not points to detect direction
            # TODO: add log to register this situations
            logger = logging.getLogger(__name__)
            logger.info("There is not position to detect bus direction")
            return "left"

        epsilon = 0.00008
        x1 = lower.longitude
        # y1 = lower.latitude
        x2 = greater.longitude
        # y2 = greater.latitude

        if abs(x2 - x1) >= epsilon:
            if x2 - x1 > 0:
                return "right"
            else:
                return "left"
        else:
            # we compare bus location with bus stop location
            xBusStop = stopObj.longitude
            if x2 - xBusStop > 0:
                return "left"
            else:
                return "right"

    def getLocation(self):
        """This method estimate the location of a bus given one user that is inside or gives a geolocation estimated."""
        tokens = Token.objects.filter(busassignment=self)
        lastDate = timezone.now() - timezone.timedelta(minutes=5)
        passengers = 0
        lat = -500
        lon = -500
        random = True
        for token in tokens:
            if not hasattr(token, 'activetoken'):
                continue
            passengers += 1
            try:
                lastPose = PoseInTrajectoryOfToken.objects.filter(
                    token=token, timeStamp__gte=lastDate).latest('timeStamp')
                lastDate = lastPose.timeStamp
                lat = lastPose.latitude
                lon = lastPose.longitude
                random = False
            except PoseInTrajectoryOfToken.DoesNotExist:
                logger = logging.getLogger(__name__)
                logger.info("There is not geolocation in the last 5 minutes. token: {} | time: {}". \
                            format(token.token, timezone.now()))

        return {'latitude': lat,
                'longitude': lon,
                'passengers': passengers,
                'random': random
                }

    def getEstimatedLocation(self, stopCode, distance):
        """Given a distace from the bus to the busstop, this method returns the global position of the machine."""
        try:
            serviceCode = ServicesByBusStop.objects.filter(
                busStop__code=stopCode, service__service=self.service,
                gtfs__version=settings.GTFS_VERSION).values_list('code', flat=True)[0]
        except ServicesByBusStop.DoesNotExist:
            raise ServiceNotFoundException(
                "Service {} is not present in bus stop {}".format(
                    self.service, stopCode))

        ssd = ServiceStopDistance.objects.filter(
            busStop__code=stopCode, service=serviceCode,
            gtfs__version=settings.GTFS_VERSION).values_list('distance', flat=True)[0] - int(distance)

        try:
            closest_gt = ServiceLocation.objects.filter(
                service=serviceCode,
                gtfs__version=settings.GTFS_VERSION,
                distance__gte=ssd).order_by('distance').value_list('distance', flat=True)[0]
        except:
            closest_gt = 50000
        try:
            closest_lt = ServiceLocation.objects.filter(
                service=serviceCode,
                gtfs__version=settings.GTFS_VERSION,
                distance__lte=ssd).order_by('-distance').values_list('distance', flat=True)[0]
        except:
            closest_lt = 0

        if abs(closest_gt - ssd) < abs(closest_lt - ssd):
            closest = closest_gt
        else:
            closest = closest_lt

        location = ServiceLocation.objects.filter(
            service=serviceCode,
            gtfs__version=settings.GTFS_VERSION,
            distance=closest).first()

        return {'latitude': location.latitude,
                'longitude': location.longitude,
                'direction': serviceCode[-1]
                }


class Token(models.Model):
    """This table has all the tokens that have been used ever."""
    token = models.CharField('Token', max_length=128)
    """Identifier for an incognito trip"""
    busassignment = models.ForeignKey(Busassignment, verbose_name='Bus')
    """Bus that is making the trip"""
    direction = models.CharField(max_length=1, null=True)
    """ route direction that the bus is doing. It can be 'R' or 'I' """
    color = models.CharField("Icon's color", max_length=7, default='#00a0f0')
    """Color to paint the travel icon"""
    phoneId = models.UUIDField()
    """ To identify the data owner """
    timeCreation = models.DateTimeField('Time Creation', null=True, blank=False)
    """ creation time of token """
    userEvaluation = models.IntegerField(null=True)
    """ User evaluation does at the end of trip """
    tranSappUser = models.ForeignKey('TranSappUser', null=True)
    """ Logged user with social media (if exists) """
    USER_SAYS_GET_OFF = 'user'
    SERVER_SAYS_GET_OFF = 'server'
    SERVER_DOES_NOT_RECEIVE_LOCATIONS = 'cron_finished_trip'
    SMARTPHONE_SAYS_IS_FAR_AWAY_FROM_REAL_BUS = 'phone_far_away'
    SMARTPHONE_SAYS_THAT_THERE_IS_NOT_MOVEMENT = 'phone_still'
    PURGE_CAUSE_CHOICES = (
        (USER_SAYS_GET_OFF, 'user says get off'),
        (SERVER_SAYS_GET_OFF, 'server says get off'),
        (SERVER_DOES_NOT_RECEIVE_LOCATIONS, 'cron finished trip'),
        (SMARTPHONE_SAYS_IS_FAR_AWAY_FROM_REAL_BUS, 'smartphone says that is far away from real bus'),
        (SMARTPHONE_SAYS_THAT_THERE_IS_NOT_MOVEMENT, 'smartphone says that there is not movement')
    )
    purgeCause = models.CharField(max_length=50, null=True, choices=PURGE_CAUSE_CHOICES)
    """ To know why trip finished """

    def get_distance_to(self, longitude, latitude):
        """ it calculates distance between last point saved in poseTrajectoryOfToken and point given. It returns
        distance in meters """

        if self.poseintrajectoryoftoken_set.count() > 0:
            bus_location = self.poseintrajectoryoftoken_set.all().order_by("-timeStamp").first()
            return round(haversine(bus_location.longitude, bus_location.latitude, longitude, latitude), 2)
        return 0


class PoseInTrajectoryOfToken(Location):
    """This stores all the poses of a trajectory. The trajectory can start on foot and end on foot."""
    IN_VEHICLE = 'vehicle'
    NON_VEHICLE = 'non_vehicle'
    timeStamp = models.DateTimeField(null=False, blank=False, db_index=True)
    """ Specific date time when the server received a pose in the trajectory """
    inVehicleOrNot = models.CharField(max_length=15)  # vehicle, non_vehicle
    """ Identify if a pose was sended inside a vehicle or not """
    token = models.ForeignKey(Token, verbose_name='Token')

    class Meta:
        index_together = ["token", "timeStamp"]


class ActiveToken(models.Model):
    """This are the tokens that are currently beeing use to upload positions."""
    timeStamp = models.DateTimeField('Time Stamp', null=False, blank=False)
    """ Specific date time when the server received the first pose in the trajectory, i.e. when the trip started """
    token = models.OneToOneField(Token, verbose_name='Token')


class Report(models.Model):
    """ This is the free report, it saves the message and the picture location in the system """
    timeStamp = models.DateTimeField(null=False, blank=False, db_index=True)
    """ Specific date time when the server received a pose in the trajectory """
    message = models.TextField()
    """ Text reported by the user """
    imageName = models.CharField(max_length=100, default=None, null=True)
    """ image name that was saved """
    imageFile = models.FileField(upload_to='reported_images', default=None, null=True)
    """ image file """
    reportInfo = models.TextField()
    """ Aditinal information regarding the report. For example the user location."""
    phoneId = models.UUIDField()
    """ To identify the data owner """
    tranSappUser = models.ForeignKey('TranSappUser', null=True)
    """ Logged user with social media (if exists) """

##
#
# Log for some requests
#
##


class NearByBusesLog(models.Model):
    """ Register user request for bus stop """
    timeStamp = models.DateTimeField('Time Stamp', null=False, blank=False)
    """ Specific date time when the server received the request """
    busStop = models.ForeignKey(BusStop, verbose_name='Bus Stop')
    """ Bus stops where the service is stopped """
    phoneId = models.UUIDField()
    """ To identify the data owner """


##
#
# score and login
#
##


class Level(models.Model):
    """ user level """
    name = models.CharField(max_length=50, null=False, blank=False)
    """ level name """
    minScore = models.FloatField(default=0, null=False)
    """ minimun score to keep the level """
    maxScore = models.FloatField(default=0, null=False)
    """ maximum score to keep the level """
    position = models.IntegerField(null=False, unique=True)
    """ to order levels 1,2,3,... """

    def getDictionary(self):
        return  {
            "name": self.name,
            "maxScore": self.maxScore,
            "minScore": self.minScore,
            "position": self.position
        }


class TranSappUser(models.Model):
    """ user logged with social network (Facebook, google) """
    userId = models.CharField(max_length=128, null=False, blank=False)
    """ user id given by social network(FacebookUserId or ) """
    name = models.CharField(max_length=50, null=False, blank=False)
    """ user name """
    email = models.EmailField(null=False, blank=False)
    """ user email"""
    phoneId = models.UUIDField(null=False)
    """ phone id used to log in """
    FACEBOOK = 'FACEBOOK'
    GOOGLE = 'GOOGLE'
    ACCOUNT_TYPES = (
        (FACEBOOK, 'Facebook'),
        (GOOGLE, 'Google')
    )
    accountType = models.CharField(max_length=10, choices=ACCOUNT_TYPES, null=False)
    """ type of toke id (it says where tokenID comes from) """
    globalScore = models.FloatField(default=0, null=False)
    """ global score generated by user interactions """
    level = models.ForeignKey(Level, null=False)
    """ level based on score """
    sessionToken = models.UUIDField(null=False)
    """ uuid generated each time the user log in """
    nickname = models.CharField(max_length=20, null=False)
    """ user nick name """
    photoURI = models.URLField(null=False)
    """ social media photo """
    userAvatarId = models.IntegerField(default=1)
    """ avatar used to hide identity of user """
    showAvatar = models.BooleanField(default=True)
    """ to indicate if system hast to use the avatar or social media photo """
    busAvatarId = models.IntegerField(default=1)
    """ bus avatar used to show buses on app map """
    externalId = models.UUIDField(default=uuid.uuid4, unique=True, null=False)
    """ user external id """
    globalPosition = models.BigIntegerField()
    """ global position betweenn TranSapp users """
    timeCreation = models.DateTimeField(default=timezone.now, null=False)
    """ time when user was created """
    timestamp = models.DateTimeField(default=timezone.now, null=False)
    """ last time when user opened app while is logged """

    def getDictionary(self):
        """ get dictionary of public data """
        data = {
            "nickname": self.nickname,
            "globalScore": round(self.globalScore, 8),
            "showAvatar": self.showAvatar,
            "levelName": self.level.name,
            "levelPosition": self.level.position,
            "id": self.externalId,
            "ranking": {
                "globalPosition": self.globalPosition
            }
        }
        if self.showAvatar:
            data['userAvatarId'] = self.userAvatarId
        else:
            data["photoURI"] = self.photoURI

        return data

    def getScoreData(self):
        """ return updated score data """
        return {
            "id": self.externalId,
            "score": round(self.globalScore, 8),
            "ranking": {
                "globalPosition": self.globalPosition
            },
            "level": self.level.getDictionary()
        }

    def getLoginData(self):
        """ return user info needed when finish login process """
        return {
            "userData": self.getScoreData(),
            "userSettings": {
                "busAvatarId": self.busAvatarId,
                "userAvatarId": self.userAvatarId,
                "showAvatar": self.showAvatar
            }
        }


class ScoreEvent(models.Model):
    """ score given by action """
    code = models.CharField(max_length=10, null=False, blank=False, unique=True)
    """ event code """
    score = models.FloatField(default=0, null=False)
    """ score given to user when he does the action associated to code """


class ScoreHistory(models.Model):
    """ history of events give score """
    tranSappUser = models.ForeignKey(TranSappUser)
    """ user """
    scoreEvent = models.ForeignKey(ScoreEvent)
    """ event that generates the score """
    timeCreation = models.DateTimeField(null=False)
    """ time when event was generated """
    score = models.FloatField(default=0, null=False)
    """ wined score """
    meta = models.TextField(null=True)
    """ additional data to score """
