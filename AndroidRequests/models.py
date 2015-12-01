from django.db import models
from django.utils import timezone

# Create your models here.
# Remembre to add new models to admin.py

class Location(models.Model):
	""" Some of our models require to set a geolocation (coodinates)"""
	longitud = models.FloatField('Longitude', null=False, blank=False)
	""" longitude from the geolocation """
	latitud = models.FloatField('Latitude', null=False, blank=False)
	""" longitude from the geolocation """

	class Meta:
		"""This makes that the fields here define are added to the tables that
		extends this, and no ForeignKey is made."""
		abstract = True

class DevicePositionInTime(Location):	
	"""Helps storing the position of active users"""
	timeStamp = models.DateTimeField(null=False, blank=False)
	""" longitude from the geolocation """

class Event(models.Model):
	"""Here are all the events, its configurarion and info."""
	id = models.CharField(max_length=8, primary_key = True)
	name = models.CharField(max_length=30, null=False, blank=False)
	description = models.CharField(max_length=140, null=True)
	lifespam = models.IntegerField(default=30)# this value is in minutes
	category = models.CharField(max_length=20)

	REPORT_ORIGIN = (
		('i','the event was taken insede the bus'), # is an I from inside
		('o','the event was taken from a bustop'),) # this is an O from outside
	REPORT_TYPE = (
		('bus','An event for the bus.'),
		('busStop','An event for the busStop.'))
	origin = models.CharField(max_length=1, choices=REPORT_ORIGIN, default='o')
	eventType = models.CharField(max_length=7, choices=REPORT_TYPE)

	def getDictionary(self):
		"""Return a dictionary whit information of the event."""
		dictionary = {}
		dictionary['name'] = self.name
		dictionary['description'] = self.description
		dictionary['eventcode'] = self.id
		return dictionary

##
#
# This are the modles to handel the registration of events for a bus or a busstop
#
##
class StadisticDataFromRegistration(Location):
	timeStamp = models.DateTimeField(null=False, blank=False)
	confirmDecline = models.CharField(max_length=10)

	class Meta:
		abstract = True

class StadisticDataFromRegistrationBus(StadisticDataFromRegistration):
	reportOfEvent = models.ForeignKey('EventForBus')

class StadisticDataFromRegistrationBusStop(StadisticDataFromRegistration):
	reportOfEvent = models.ForeignKey('EventForBusStop')

class EventRegistration(models.Model):
	'''This model stores the reposts of events coming from the  
	passagers of the public Bus transport system.'''
	timeStamp = models.DateTimeField() # lastime it was updated
	timeCreation = models.DateTimeField() # the date and time when it was first reported
	event = models.ForeignKey(Event, verbose_name='The event information')
	eventConfirm = models.IntegerField(default=1)
	eventDecline = models.IntegerField(default=0)

	class Meta:
		abstract = True

	def getDictionary(self):
		'''A doctionary whit info of the event, not all only what was of interest
		to return to the app.'''
		dictionary = {}

		dictionary['eventConfirm'] = self.eventConfirm
		dictionary['eventDecline'] = self.eventDecline
		dictionary['timeCreation'] = '%i-%i-%i %i:%i:%i' % (self.timeCreation.day, self.timeCreation.month,\
			self.timeCreation.year, self.timeCreation.hour, self.timeCreation.minute, self.timeCreation.second)
		dictionary['timeStamp'] = '%i-%i-%i %i:%i:%i' % (self.timeStamp.day, self.timeStamp.month,\
			self.timeStamp.year, self.timeStamp.hour, self.timeStamp.minute, self.timeStamp.second)
		eventDictionay = self.event.getDictionary()
		dictionary.update(eventDictionay)

		return dictionary

class EventForBusStop(EventRegistration):
	'''This model stores the reported events for the busStop'''
	busStop = models.ForeignKey('BusStop', verbose_name='The bustop')
	aditionalInfo = models.CharField(max_length=140, default='nothing')


class EventForBus(EventRegistration):
	'''This model stores the reported events for the Bus'''
	bus = models.ForeignKey('Bus', verbose_name='the bus')


##
#
# The end for the model for the registration
#
##

class ServicesByBusStop(models.Model):
	"""This model helps to determin the direction of the bus service I or R.
	All of this is tide to the bus stop code and the service provided by it.
	It's usefull to hace the direction of the service to been able to determin
	position of the bus."""
	code = models.CharField(max_length=6, null=False, blank=False) # EX: 506I or 506R, R and I indicate "Ida" and "Retorno"
	busStop = models.ForeignKey('BusStop', verbose_name='the busStop')
	service = models.ForeignKey('Service', verbose_name='the service')


class BusStop(Location):
	"""Represents the busStop itself."""
	code = models.CharField(max_length=6, primary_key = True) # For example PA443
	name = models.CharField(max_length=70, null = False, blank = False)
	events = models.ManyToManyField(Event, verbose_name='the event' ,through=EventForBusStop)

	def getDictionary(self):
		"""usefull information regarding the bus."""
		dictionary = {}

		dictionary['codeBusStop'] = self.code
		dictionary['nameBusStop'] = self.name

		return dictionary


class Service(models.Model):
	""" Represent a Service like '506' and save his data """
	service = models.CharField(max_length=5, primary_key = True)
	origin = models.CharField(max_length=100, null=False, blank=False)
	destiny = models.CharField(max_length=100, null=False, blank=False)
	color = models.CharField(max_length=7, default='#00a0f0')
	color_id = models.IntegerField(default = 0)
	busStops = models.ManyToManyField(BusStop, verbose_name='the Bus Stop' ,through=ServicesByBusStop)

class Bus(models.Model):
	"""The bus. The bus is consideres the unique combination of registration plate and service as one.
	So there can be two buses whit same service (da) and two buses whit same registration plate.
	The last thing means that one fisical bus can work in two different service."""
	registrationPlate = models.CharField(max_length=8)
	service = models.CharField(max_length=5, null=False, blank=False)
	events = models.ManyToManyField(Event,  verbose_name='the event' ,through=EventForBus)

	class Meta:
		unique_together = ('registrationPlate', 'service')

	def getDirection(self, pBusStop, pDistance):
		import math
		try:
			serviceCode = ServicesByBusStop.objects.get(busStop = pBusStop, service = self.service).code
		except:
			serviceCode = self.service + "I"
		
		distance = ServiceStopDistance.objects.get(busStop = pBusStop, service = serviceCode).distance - int(pDistance)
		greaters = ServiceLocation.objects.filter(service = serviceCode, distance__gt=distance).order_by('distance')
		lowers = ServiceLocation.objects.filter(service = serviceCode, distance__lte=distance).order_by('-distance')
		try:
			greater = greaters[0]
		except:
			greater = lowers[0]
			lower = lowers[1]
		else:
			try:
				lower = lowers[0]
			except:
				lower = greater
				greater = greaters[1]
		epsilon = 0.00008
		x1 = lower.longitud
		y1 = lower.latitud
		x2 = greater.longitud
		y2 = greater.latitud
		if(abs(x2-x1)>=epsilon):
			if(x2-x1>0):
				return "right"
			else:
				return "left"
		else:
			if(y2-y1>0):
				return "up"
			else:
				return "down"


	def getLocation(self, busstop, distance):
		"""This method estimate the location of a bus given one user that is inside or gives the location estimated by
		transantiago."""
		from random import uniform
		tokens = Token.objects.filter(bus=self)
		lastDate = timezone.now()-timezone.timedelta(days=30)
		passengers = 0
		lat = -500
		lon = -500 
		for token in tokens:
			if(not hasattr(token, 'activetoken')):
				continue
			passengers += 1
			trajectoryQuery = PoseInTrajectoryOfToken.objects.filter(token = token)
			if trajectoryQuery.exists():
				lastPose = trajectoryQuery.latest('timeStamp');
				if (lastPose.timeStamp>=lastDate):
					lastDate = lastPose.timeStamp
					lat = lastPose.latitud
					lon = lastPose.longitud
		if(lat == lon and lat == -500):
			try:
				return self.__estimatedPosition(busstop, distance, passengers)

			except:
				return {'latitud': -33.427690 + uniform(0.000000, 0.0005),
						'longitud': -70.434710 + uniform(0.000000, 0.0005),
						'passengers': passengers, 
						'random':True}
		return {'latitud': lat,
				'longitud': lon,
				'passengers': passengers,
				'random': False
				}

	def __estimatedPosition(self, busstop, distance, passengers):
		'''Given a distace from the bus to the busstop, this method returns the global position of
		the machine.'''
		try:
			serviceCode = ServicesByBusStop.objects.get(busStop = busstop, service = self.service).code
		except:
			serviceCode = self.service + "I"
			
		ssd = ServiceStopDistance.objects.get(busStop = busstop, service = serviceCode).distance - int(distance)

		try:
			closest_gt = ServiceLocation.objects.filter(service = serviceCode, distance__gte=ssd).order_by('distance')[0].distance
		except:
			closest_gt = 50000
		try:
			closest_lt = ServiceLocation.objects.filter(service = serviceCode, distance__lte=ssd).order_by('-distance')[0].distance
		except:
			closest_lt = 0

		if(abs(closest_gt-ssd) < abs(closest_lt-ssd)):
			closest = closest_gt
		else:
			closest = closest_lt
		location = ServiceLocation.objects.filter(service = serviceCode, distance = closest)[0]
		return {'latitud': location.latitud,
				'longitud': location.longitud,
				'passengers': passengers,
				'random': False
				}

	def getDictionary(self):
		dictionary = {}

		dictionary['serviceBus'] = self.service
		dictionary['registrationPlateBus'] = self.registrationPlate

		return dictionary

class ServiceLocation(Location):
	'''This models stores the position allong the route of every bus at 10 meters apart. 
	You can give the distance form the start of the travel and it return the position at 
	that distance.'''
	service = models.CharField(max_length=6, null=False, blank=False) #Service code i.e. 506I or 506R
	distance = models.IntegerField()

	class Meta:
		index_together = ["service", "distance"]

class ServiceStopDistance(models.Model):
	'''This model stores the distance for every bustop in every bus rout for every service.
	Given a bus direction code xxxI or xxR or something alike.'''
	busStop = models.ForeignKey(BusStop)
	service = models.CharField(max_length=6, null=False, blank=False) #Service code i.e. 506I or 506R
	distance = models.IntegerField()


class Token(models.Model):
	'''This table has all the tokens the have ever beeing used.'''
	token = models.CharField(max_length=128, primary_key=True)
	bus = models.ForeignKey(Bus)
	color = models.CharField(max_length=7, default='#00a0f0')

class PoseInTrajectoryOfToken(Location):
	'''This stores all the poses of a trajectory. The trajectory can start on foot and end on foot.'''
	timeStamp = models.DateTimeField(null=False, blank=False, db_index=True)
	inVehicleOrNot =models.CharField(max_length=15) # vehicle, non_vehicle
	token = models.ForeignKey(Token)
	
	class Meta:
		index_together = ["token", "timeStamp"]

class ActiveToken(models.Model):
	'''This are the tokens that are currently beeing use to upload positions.'''
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.OneToOneField(Token)

class Report(models.Model):
	""" This is the free report, it save the message and the picture location in the system  """
	message = models.TextField()
	path = models.CharField(max_length=500, default="no image")
