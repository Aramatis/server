from django.db import models

# Create your models here.

class DevicePositionInTime(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)
	timeStamp = models.DateTimeField(null=False, blank=False)

class Event(models.Model):
	id = models.CharField(max_length=8, primary_key = True)
	name = models.CharField(max_length=30, null=False, blank=False)

class BusStop(models.Model):
	code = models.CharField(max_length=6, primary_key = True)
	name = models.CharField(max_length=30, null = False, blank = False)
	events = models.ManyToManyField(Event)

class Bus(models.Model):
	registrationPlate = models.CharField(max_length=8, primary_key = True)
	service = models.CharField(max_length=5, null=False, blank=False)
	events = models.ManyToManyField(Event)

class Token(models.Model):
	token = models.CharField(max_length=128, primary_key=True)
	bus = models.ForeignKey(Bus)
	color = models.CharField(max_length=7, default='#00a0f0')

class PoseInTrajectoryOfToken(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.ForeignKey(Token)

class ActiveToken(models.Model):
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.ForeignKey(Token)