from django.db import models

# Create your models here.

class Log(models.Model):
    """ register a call to dtpm """
    busStopCode = models.CharField(max_length=6, null=False)
    """ user code of bus stop """
    serverTimeStamp = models.DateTimeField(null=False)
    """ server time when it received DTPM answer """
    dtpmTimeStamp = models.DateTimeField(null=False)
    """ time when DTPM server made the answer """
    webTransId = models.CharField(max_length=24, null=False, db_index=True)
    """ transaction id used to request DTPM server """
    errorMessage = models.TextField(null=True)
    """ error message returned by DTPM """

class BusLog(models.Model):
    """ register buses gotten from dtpm  """
    licensePlate = models.CharField(max_length=7, null=False)
    """ licence plate of bus """
    serviceName = models.CharField(max_length=7, null=False)
    """ The service which goes to bus stop  """
    timeMessage = models.CharField(max_length=50, null=False)
    """ Time to wait the bus arrival to bus stop"""
    distance = models.IntegerField(null=False)
    """ Distance from bus to bus stop """
    valid = models.CharField(max_length=1, null=False)
    """ It says if the information received is correct """
    log = models.ForeignKey('Log', on_delete = models.CASCADE)
    """ Foreign key """
