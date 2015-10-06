from django.db import models

# Create your models here.

class DevicePositionInTime(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)
	timeStamp = models.DateTimeField(null=False, blank=False)

class PoseInTrajectoryOfToken(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.CharField(max_length=128, null = False, blank=False)

class ActiveToken(models.Model):
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.CharField(max_length=128, primary_key=True)