from django.db import models

# Create your models here.

class DevicePositionInTime(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)
	timeStamp = models.DateTimeField(null=False, blank=False)

class Token(models.Model):
	token = models.CharField(max_length=128, primary_key=True)
	busService = models.CharField(max_length=5, null=False, blank=False)
	busRegistrationPlate = models.CharField(max_length=8)
	color = models.CharField(max_length=7, default='#00a0f0')

class PoseInTrajectoryOfToken(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.ForeignKey(Token)

class ActiveToken(models.Model):
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.ForeignKey(Token)
