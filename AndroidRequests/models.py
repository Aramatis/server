from django.db import models
from django.utils import timezone

# Create your models here.

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


class ServicesByBusStop(models.Model):
	busStop = models.ForeignKey(BusStop)
	code = models.CharField(max_length=6, null=False, blank=False) # EX: 506I or 506R, R and I indicate "Ida" y "Retorno"
	service = models.CharField(max_length=5, null=False, blank=False)

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
			return self.__estimatedPosition(busstop, distance)
		return {'latitud': lat,
				'longitud': lon,
				'estimated': False
				}

	def __estimatedPosition(self, busstop, distance):
		ssd = ServiceStopDistance.objects.get(busStop = busstop, service = self.service).distance - int(distance)
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
		location = ServiceLocation.objects.filter(service = self.service, distance = closest)[0]
		return {'latitud': location.latitud,
				'longitud': location.longitud,
				'estimated': True
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
	#TODO: cambiar nombre campo sender
	timeStamp = models.DateTimeField(null=False, blank=False)
	sender =models.CharField(max_length=15)
	token = models.ForeignKey(Token)

class ActiveToken(models.Model):
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.OneToOneField(Token)
