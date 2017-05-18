import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings

import logging

'''
Dealing with no UUID serialization support in json
'''
from json import JSONEncoder
from uuid import UUID

JSONEncoder_olddefault = JSONEncoder.default


def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID):
        return str(o)
    return JSONEncoder_olddefault(self, o)


JSONEncoder.default = JSONEncoder_newdefault

# Create your models here.
# Remembre to add new models to admin.py

class Location(models.Model):
    """ Some of our models require to set a geolocation (coodinates)"""
    longitude = models.FloatField('Longitude', null=False, blank=False)
    """ longitude from the geolocation """
    latitude = models.FloatField('Latitude', null=False, blank=False)
    """ longitude from the geolocation """

    class Meta:
        """This makes that the fields here define are added to the tables that
        extends this, and no ForeignKey is made."""
        abstract = True


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
    REPORT_TYPE = (
        ('bus', 'An event for the bus.'),
        ('busStop', 'An event for the busStop.'))
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
        dictionary = {}
        dictionary['name'] = self.name
        dictionary['description'] = self.description
        dictionary['eventcode'] = self.id
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
    ''' logged user in app that made the report '''

    class Meta:
        abstract = True

    def getDictionary(self):
        ''' return two list: one with confirm users and another with decline users '''
        result = {}
        keyName = 'declineUser'
        if self.confirmDecline == 'confirm':
            keyName = 'confirmUser'

        if self.tranSappUser is not None:
            result[keyName] = self.tranSappUser.getDictionary()
        else:
            result[keyName] = None

        return result

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
    '''This model stores the reports of events coming from the passagers of the system of public transport buses.'''
    timeStamp = models.DateTimeField('Time Stamp')  # lastime it was updated
    """ Specific date time when the server received the event registration """
    timeCreation = models.DateTimeField('Creation Time')
    """ Specific date time when the server received for the first time the event registration """
    expireTime = models.DateTimeField(null=True)
    ''' Specific date time when event expired '''
    event = models.ForeignKey(Event, verbose_name='The event information')
    eventConfirm = models.IntegerField('Confirmations', default=1)
    """ Amount of confirmations for this event """
    eventDecline = models.IntegerField('Declines', default=0)
    """ amount of declinations for this event """
    phoneId = models.UUIDField()
    """ To identify the data owner """
    broken = models.BooleanField(default=False)
    ''' to indecate that event expired by some brokenType '''
    # list  of criterion of broken type
    PERCENTAGE_BETWEEN_POSITIVE_AND_NEGATIVE = 'percentage'
    brokenType = models.CharField(max_length=50, default=None, null=True)
    ''' indicate why event is broken '''

    class Meta:
        abstract = True

    def getDictionary(self):
        '''A dictionary with the event information, just what was of interest to return to the app.'''
        dictionary = {}

        dictionary['eventConfirm'] = self.eventConfirm
        dictionary['eventDecline'] = self.eventDecline
        creation = timezone.localtime(self.timeCreation)
        stamp = timezone.localtime(self.timeStamp)
        dictionary['timeCreation'] = creation.strftime("%d-%m-%Y %H:%M:%S")
        dictionary['timeStamp'] = stamp.strftime("%d-%m-%Y %H:%M:%S")
        eventDictionay = self.event.getDictionary()
        dictionary.update(eventDictionay)

        return dictionary

class EventForBusStop(EventRegistration):
    '''This model stores the reported events for the busStop'''
    stopCode = models.CharField(max_length=6, db_index=True, verbose_name='Stop Code')
    '''Indicates the bus stop to which the event refers'''
    aditionalInfo = models.CharField(
        'Additional Information',
        max_length=140,
        default='nothing')
    ''' Saves additional information required by the event '''


class EventForBusv2(EventRegistration):
    '''This model stores the reported events for the Bus'''
    busassignment = models.ForeignKey('Busassignment', verbose_name='the bus')
    '''Indicates the bus to which the event refers'''

##
#
# The end for the model for the registration
#
##


class ServicesByBusStop(models.Model):
    """This model helps to determine the direction of the bus service I or R.
    All of this is tied to the bus stop code and the service provided by it.
    It's useful to have the direction of the service to be able to determine position of the bus."""
    code = models.CharField(
        max_length=11,
        null=False,
        blank=False)  # EX: 506I or 506R, R and I indicate "Ida" and "Retorno"
    """ Service code where the last character indicates the direction of this """
    busStop = models.ForeignKey('BusStop', verbose_name='the busStop')
    """ Bus stops where the service is stopped """
    service = models.ForeignKey('Service', verbose_name='the service')
    """ Service that stops in the bus stop """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        unique_together = ('code', 'busStop', 'gtfs')


class BusStop(Location):
    """Represents the busStop itself."""
    code = models.CharField(
        'Code',
        max_length=6)
    """ Code that identifies the bus stop """
    name = models.CharField('Name', max_length=70, null=False, blank=False)
    """ Name of the bus stop, indicating the streets """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    def getDictionary(self):
        """usefull information regarding the bus."""
        dictionary = {}

        dictionary['codeBusStop'] = self.code
        dictionary['nameBusStop'] = self.name

        return dictionary

    class Meta:
        unique_together = ('code', 'gtfs')

class Service(models.Model):
    """ Represent a Service like '506' and save his data """
    service = models.CharField('Service', max_length=11)
    """ Represent the service, like '506c' without direction """
    origin = models.CharField(max_length=100, null=False, blank=False)
    """ Indicates the place where the service start his travel """
    destiny = models.CharField(max_length=100, null=False, blank=False)
    """ Indicates the place where the service end his travel """
    color = models.CharField(max_length=7, default='#00a0f0')
    """ Indicates the color in hexadecimal for the service """
    color_id = models.IntegerField(default=0)
    """ Represent an index for a color array in the app """
    busStops = models.ManyToManyField(
        BusStop,
        verbose_name='Bus Stops',
        through=ServicesByBusStop)
    """ bus stops where the service stops """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        unique_together = ('service', 'gtfs')


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

    def getDirection(self, pBusStop, pDistance):
        """ Given a bus stop and the distance from the bus to the bus stop, return the address to which point the bus """
        try:
            serviceCode = ServicesByBusStop.objects.get(
                busStop__code=pBusStop, 
                service__service=self.service,
                gtfs__version=settings.GTFS_VERSION).code
        except ServicesByBusStop.DoesNotExist:
            raise ServiceNotFoundException(
                "Service {} is not present in bus stop {}".format(
                    self.service, pBusStop))

        try:
            serviceDistance = ServiceStopDistance.objects.get(
                busStop__code=pBusStop, 
                service=serviceCode, 
                gtfs__version=settings.GTFS_VERSION).distance
        except ServiceStopDistance.DoesNotExist:
            raise ServiceDistanceNotFoundException(
                "The distance is not possible getting for bus stop '{}' and service '{}'".format(
                    pBusStop, serviceCode))

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

        if(abs(x2 - x1) >= epsilon):
            if(x2 - x1 > 0):
                return "right"
            else:
                return "left"
        else:
            # we compare bus location with bus stop location
            busStopObj = BusStop.objects.get(code=pBusStop, 
                    gtfs__version=settings.GTFS_VERSION)
            xBusStop = busStopObj.longitude
            if(x2 - xBusStop > 0):
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
            if(not hasattr(token, 'activetoken')):
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
                logger.info("There is not geolocation in the last 5 minutes. token: {} | time: {}".format(token.token, timezone.now()))

        return {'latitude': lat,
                'longitude': lon,
                'passengers': passengers,
                'random': random
                }

    def getEstimatedLocation(self, stopCode, distance):
        '''Given a distace from the bus to the busstop, this method returns the global position of the machine.'''
        try:
            serviceCode = ServicesByBusStop.objects.get(
                busStop__code=stopCode, service__service=self.service, 
                gtfs__version=settings.GTFS_VERSION).code
        except ServicesByBusStop.DoesNotExist:
            raise ServiceNotFoundException(
                "Service {} is not present in bus stop {}".format(
                    self.service, stopCode))

        ssd = ServiceStopDistance.objects.get(
            busStop__code=stopCode, service=serviceCode, 
            gtfs__version=settings.GTFS_VERSION).distance - int(distance)

        try:
            closest_gt = ServiceLocation.objects.filter(
                service=serviceCode, 
                gtfs__version=settings.GTFS_VERSION, 
                distance__gte=ssd).order_by('distance')[0].distance
        except:
            closest_gt = 50000
        try:
            closest_lt = ServiceLocation.objects.filter(
                service=serviceCode, 
                gtfs__version=settings.GTFS_VERSION, 
                distance__lte=ssd).order_by('-distance')[0].distance
        except:
            closest_lt = 0

        if(abs(closest_gt - ssd) < abs(closest_lt - ssd)):
            closest = closest_gt
        else:
            closest = closest_lt

        location = ServiceLocation.objects.filter(
            service=serviceCode, 
            gtfs__version=settings.GTFS_VERSION, 
            distance=closest)[0]

        return {'latitude': location.latitude,
                'longitude': location.longitude,
                'direction': serviceCode[-1]
                }
    """
    def getDictionary(self):
        ''' Return a dictionary with useful information about the bus '''
        dictionary = {}

        dictionary['serviceBus'] = self.service
        dictionary['registrationPlateBus'] = self.uuid.registrationPlate

        return dictionary
    """


class ServiceLocation(Location):
    '''This models stores the position along the route of every bus at 20 meters apart.
    You can give the distance from the start of the travel and it return the position at that distance.'''
    service = models.CharField(
        'Service Code',
        max_length=11,
        null=False,
        blank=False)  # Service code i.e. 506I or 506R
    """ Service code where the last character indicates its direction """
    distance = models.IntegerField('Route Distance')
    """ Distance traveled by the service since its origin """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        index_together = ["service", "distance"]
        unique_together = ('service', 'distance', 'gtfs')


class ServiceStopDistance(models.Model):
    '''This model stores the distance for every bustop in every bus route for every service.
    Given a bus direction code xxxI or xxxR or something alike.'''
    busStop = models.ForeignKey(BusStop, verbose_name='Bus Stop')
    """ Bus stops where the service is stopped """
    service = models.CharField(
        'Service Code',
        max_length=11,
        null=False,
        blank=False)  # Service code i.e. 506I or 506R
    """ It represents the Service code, ex: '506I' """
    distance = models.IntegerField('Distance Traveled')
    """ Distance traveled by the service when it reaches the bus stop """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """
    class Meta:
        unique_together = ('busStop', 'service', 'gtfs')


class Token(models.Model):
    '''This table has all the tokens that have been used ever.'''
    token = models.CharField('Token', max_length=128)
    '''Identifier for an incognito trip'''
    busassignment = models.ForeignKey(Busassignment, verbose_name='Bus')
    '''Bus that is making the trip'''
    direction = models.CharField(max_length=1, null=True)
    ''' route direction that the bus is doing. It can be 'R' or 'I' '''
    color = models.CharField("Icon's color", max_length=7, default='#00a0f0')
    '''Color to paint the travel icon'''
    phoneId = models.UUIDField()
    """ To identify the data owner """
    timeCreation = models.DateTimeField('Time Creation', null=True, blank=False)
    """ creation time of token """
    userEvaluation = models.IntegerField(null=True)
    """ User evaluation does at the end of trip """
    # uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # ''' UUID to identify a dummy bus'''

    def getBusesIn(self, pListOfServices):
        """ return a list of buses that match with buses given as parameter """


class PoseInTrajectoryOfToken(Location):
    '''This stores all the poses of a trajectory. The trajectory can start on foot and end on foot.'''
    timeStamp = models.DateTimeField(null=False, blank=False, db_index=True)
    """ Specific date time when the server received a pose in the trajectory """
    inVehicleOrNot = models.CharField(max_length=15)  # vehicle, non_vehicle
    """ Identify if a pose was sended inside a vehicle or not """
    token = models.ForeignKey(Token, verbose_name='Token')

    class Meta:
        index_together = ["token", "timeStamp"]


class ActiveToken(models.Model):
    '''This are the tokens that are currently beeing use to upload positions.'''
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
    reportInfo = models.TextField()
    """ Aditinal information regarding the report. For example the user location."""
    phoneId = models.UUIDField()
    """ To identify the data owner """


class GTFS(models.Model):
    """ manage different version presents in database """
    version = models.CharField(max_length=10, default=None, null=False, unique=True)
    """ GTFS version """
    timeCreation = models.DateTimeField('Time Creation', null=True, blank=False)
    """ creation time of token """


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


class Route(Location):
    """ Route for each service """
    serviceCode = models.CharField(
        db_index=True,
        max_length=11,
        null=False,
        blank=False)
    """ Bus identifier """
    sequence = models.IntegerField('Sequence')
    """ point position in a route """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        unique_together = ('serviceCode', 'sequence', 'gtfs')

##
#
# score and login
#
##

class Level(models.Model):
    ''' user level '''
    name = models.CharField(max_length=50, null=False, blank=False)
    ''' level name '''
    minScore = models.FloatField(default=0, null=False)
    ''' minimun score to keep the level '''
    maxScore = models.FloatField(default=0, null=False)
    ''' maximum score to keep the level '''
    position = models.IntegerField(null=False, unique=True)
    ''' to order levels 1,2,3,... '''


class TranSappUser(models.Model):
    ''' user logged with social network (Facebook, google) '''
    userId = models.CharField(max_length=128, null=False, blank=False)
    ''' user id given by social network(FacebookUserId or ) '''
    name = models.CharField(max_length=50, null=False, blank=False)
    ''' user name '''
    email = models.EmailField(null=False, blank=False)
    ''' user email'''
    phoneId = models.UUIDField(null=False)
    ''' phone id used to log in '''
    FACEBOOK = 'FACEBOOK'
    GOOGLE = 'GOOGLE'
    ACCOUNT_TYPES=(
        (FACEBOOK, 'Facebook'),
        (GOOGLE, 'Google')
    )
    accountType = models.CharField(max_length=10, choices=ACCOUNT_TYPES, null=False)
    ''' type of toke id (it says where tokenID comes from) '''
    globalScore = models.FloatField(default=0, null=False)
    ''' global score generated by user interactions '''
    level = models.ForeignKey(Level, null=False)
    ''' level based on score '''
    sessionToken = models.UUIDField(null=False)
    ''' uuid generated each time the user log in '''
    nickname = models.CharField(max_length=20, null=False)
    ''' user nick name '''
    photoURI = models.URLField(null=False)
    ''' social media photo '''
    userAvatarId = models.IntegerField(default=1)
    ''' avatar used to hide identity of user '''
    showAvatar = models.BooleanField(default=True)
    ''' to inidicate if system hast to use the avatar or social media photo '''
    busAvatarId = models.IntegerField(default=1)
    ''' bus avatar used to show buses on app map '''

    def getDictionary(self):
        ''' get dictionary of public data '''
        data = {
            "nickname": self.nickname,
            "globalScore": self.globalScore,
            "showAvatar": self.showAvatar,
            "levelName": self.level.name
        }
        if self.showAvatar:
            data["photoURI"] = self.photoURI
        else:
            data['userAvatarId'] = self.userAvatarId

        return data

class ScoreEvent(models.Model):
    ''' score given by action '''
    code = models.CharField(max_length=10, null=False, blank=False, unique=True)
    ''' event code '''
    score = models.FloatField(default=0, null=False)
    ''' score given to user when he does the action associated to code '''


class ScoreHistory(models.Model):
    ''' history of events give score'''
    tranSappUser = models.ForeignKey(TranSappUser)
    ''' user '''
    scoreEvent = models.ForeignKey(ScoreEvent)
    ''' event that generates the score '''
    timeCreation = models.DateTimeField(null=False)
    ''' time when event was generated '''
    score = models.FloatField(default=0, null=False)
    ''' winned score '''
    meta = models.CharField(max_length=10000, null=True)
    ''' addional data to score '''

