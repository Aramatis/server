from django.db import models
from django.utils import timezone

# Create your models here.
# Remembre to add new models to admin.py
class Location(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)

	class Meta:
		abstract = True

class DevicePositionInTime(Location):	
	timeStamp = models.DateTimeField(null=False, blank=False)

class Event(models.Model):
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
		dictionary = {}

		dictionary['eventConfirm'] = self.eventConfirm
		dictionary['eventDecline'] = self.eventDecline
		dictionary['timeCreation'] = self.timeCreation
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
	busStop = models.ForeignKey('BusStop')
	code = models.CharField(max_length=6, null=False, blank=False) # EX: 506I or 506R, R and I indicate "Ida" and "Retorno"
	service = models.CharField(max_length=5, null=False, blank=False)

class BusStop(Location):
	code = models.CharField(max_length=6, primary_key = True)
	name = models.CharField(max_length=70, null = False, blank = False)
	events = models.ManyToManyField(Event, verbose_name='the event' ,through=EventForBusStop)

	def getDictionary(self):
		dictionary = {}

		dictionary['codeBusStop'] = self.code
		dictionary['nameBusStop'] = self.name

		return dictionary

class Bus(models.Model):
	registrationPlate = models.CharField(max_length=8)
	service = models.CharField(max_length=5, null=False, blank=False)
	events = models.ManyToManyField(Event,  verbose_name='the event' ,through=EventForBus)

	class Meta:
		unique_together = ('registrationPlate', 'service')

	def getLocation(self, busstop, distance):
		from random import uniform
		tokens = Token.objects.filter(bus=self)
		lastDate = timezone.now()-timezone.timedelta(days=30)
		lat = -500
		lon = -500 
		for token in tokens:
			if(not hasattr(token, 'activetoken')):
				continue
			lastPose = PoseInTrajectoryOfToken.objects.filter(token = token).latest('timeStamp');
			if (lastPose.timeStamp>=lastDate):
				lastDate = lastPose.timeStamp
				lat = lastPose.latitud
				lon = lastPose.longitud
		if(lat == lon and lat == -500):
			try:
				return self.__estimatedPosition(busstop, distance)
			except:
				raise
				return {'latitud': -33.456967 + uniform(0.000000, 0.0003),
						'longitud': -70.662169 + uniform(0.000000, 0.0003),
						'estimated': True, 
						'random':True}
		return {'latitud': lat,
				'longitud': lon,
				'estimated': False,
				'random': False
				}

	def __estimatedPosition(self, busstop, distance):
		serviceCode = ServicesByBusStop.objects.get(busStop = busstop, service = self.service).code
		ssd = ServiceStopDistance.objects.get(busStop = busstop, service = serviceCode).distance - int(distance)
		try:
			closest_gt = ServiceLocation.objects.filter(distance__gt=ssd).order_by('distance')[0].distance
		except:
			closest_gt = 5000000
		try:
			closest_lt = ServiceLocation.objects.filter(distance__lt=ssd).order_by('-distance')[0].distance
		except:
			closest_lt = 10
		if(abs(closest_gt-ssd) < abs(closest_lt-ssd)):
			closest = closest_gt
		else:
			closest = closest_lt
		location = ServiceLocation.objects.filter(service = serviceCode, distance = closest)[0]
		return {'latitud': location.latitud,
				'longitud': location.longitud,
				'estimated': True,
				'random': False
				}

	def getDictionary(self):
		dictionary = {}

		dictionary['serviceBus'] = self.service
		dictionary['registrationPlateBus'] = self.registrationPlate

		return dictionary

class ServiceLocation(Location):
	service = models.CharField(max_length=6, null=False, blank=False) #Service code i.e. 506I or 506R
	distance = models.IntegerField()

class ServiceStopDistance(models.Model):
	busStop = models.ForeignKey(BusStop)
	service = models.CharField(max_length=6, null=False, blank=False) #Service code i.e. 506I or 506R
	distance = models.IntegerField()


class Token(models.Model):
	token = models.CharField(max_length=128, primary_key=True)
	bus = models.ForeignKey(Bus)
	color = models.CharField(max_length=7, default='#00a0f0')

class PoseInTrajectoryOfToken(Location):
	#TODO: cambiar nombre campo sender
	timeStamp = models.DateTimeField(null=False, blank=False)
	sender =models.CharField(max_length=15) # vehicle, non_vehicle
	token = models.ForeignKey(Token)

class ActiveToken(models.Model):
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.OneToOneField(Token)
