from django.db import models

# Create your models here.

class DevicePositionInTime(models.Model):
	longitud = models.FloatField(null=False, blank=False)
	latitud = models.FloatField(null=False, blank=False)
	timeStamp = models.DateTimeField(null=False, blank=False)