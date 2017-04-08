from django.db import models

# Create your models here.


class Log(models.Model):
    """ register a call to google transit api """
    phoneId = models.UUIDField()
    """ To identify the data owner """
    origin = models.TextField(null=False)
    """ origin location """
    destination = models.TextField(null=False)
    """ destination location"""
    timeStamp = models.DateTimeField(null=True)
    """ date and time when call was done """
