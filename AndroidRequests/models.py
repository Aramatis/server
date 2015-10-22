from django.db import models
from django.utils import timezone

# Create your models here.

class Location(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)

class DevicePositionInTime(Location):	
	timeStamp = models.DateTimeField(null=False, blank=False)

class Event(models.Model):
	id = models.CharField(max_length=8, primary_key = True)
	name = models.CharField(max_length=30, null=False, blank=False)

class BusStop(Location):
	code = models.CharField(max_length=6, primary_key = True)
	name = models.CharField(max_length=70, null = False, blank = False)
	events = models.ManyToManyField(Event)

class Bus(models.Model):
	registrationPlate = models.CharField(max_length=8)
	service = models.CharField(max_length=5, null=False, blank=False)
	events = models.ManyToManyField(Event)

	class Meta:
		unique_together = ('registrationPlate', 'service')

	def getLocation(self, distance):
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
			return {'latitud': -33.456967 + uniform(0.000000, 0.000003),
					'longitud': -70.662169 + uniform(0.000000, 0.000003),
					'estimated': True
					}
		return {'latitud': lat,
				'longitud': lon,
				'estimated': False
				}

class ServiceLocation(Location):
	service = models.CharField(max_length=5, null=False, blank=False)
	distance = models.IntegerField()

class ServiceStopDistance(models.Model):
	busStop = models.ForeignKey(BusStop)
	service = models.CharField(max_length=5, null=False, blank=False)
	distance = models.IntegerField()


class Token(models.Model):
	token = models.CharField(max_length=128, primary_key=True)
	bus = models.ForeignKey(Bus)
	color = models.CharField(max_length=7, default='#00a0f0')

class PoseInTrajectoryOfToken(Location):
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.ForeignKey(Token)

class ActiveToken(models.Model):
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.OneToOneField(Token)