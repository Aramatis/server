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
	color = models.CharField(max_length=7,default='#00a0f0')

class ActiveToken(models.Model):
	color = models.CharField(max_length=7, default='#00a0f0')
	timeStamp = models.DateTimeField(null=False, blank=False)
	token = models.CharField(max_length=128, primary_key=True)