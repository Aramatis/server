# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class GTFS(models.Model):
    """ manage different version presents in database """
    version = models.CharField(max_length=10, default=None, null=False, unique=True)
    """ GTFS version """
    timeCreation = models.DateTimeField('Time Creation', null=True, blank=False)
    """ creation time of token """


class Location(models.Model):
    """ Some of our models require to set a geolocation (coodinates)"""
    longitude = models.FloatField('Longitude', null=False, blank=False)
    """ longitude from the geolocation """
    latitude = models.FloatField('Latitude', null=False, blank=False)
    """ longitude from the geolocation """

    class Meta:
        """This makes that the fields here define are added to the tables that
        extends this, and no ForeignKey is made."""
        abstract = True


class ServicesByBusStop(models.Model):
    """This model helps to determine the direction of the bus service I or R.
    All of this is tied to the bus stop code and the service provided by it.
    It's useful to have the direction of the service to be able to determine position of the bus."""
    code = models.CharField(
        max_length=11,
        null=False,
        blank=False)  # EX: 506I or 506R, R and I indicate "Ida" and "Retorno"
    """ Service code where the last character indicates the direction of this """
    busStop = models.ForeignKey('BusStop', verbose_name='the busStop')
    """ Bus stops where the service is stopped """
    service = models.ForeignKey('Service', verbose_name='the service')
    """ Service that stops in the bus stop """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        unique_together = ('code', 'busStop', 'gtfs')


class BusStop(Location):
    """Represents the busStop itself."""
    code = models.CharField(
        'Code',
        max_length=6)
    """ Code that identifies the bus stop """
    name = models.CharField('Name', max_length=70, null=False, blank=False)
    """ Name of the bus stop, indicating the streets """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    def getDictionary(self):
        """usefull information regarding the bus."""
        dictionary = {'codeBusStop': self.code, 'nameBusStop': self.name}

        return dictionary

    class Meta:
        unique_together = ('code', 'gtfs')


class Service(models.Model):
    """ Represent a Service like '506' and save his data """
    service = models.CharField('Service', max_length=11)
    """ Represent the service, like '506c' without direction """
    origin = models.CharField(max_length=100, null=False, blank=False)
    """ Indicates the place where the service start his travel """
    destiny = models.CharField(max_length=100, null=False, blank=False)
    """ Indicates the place where the service end his travel """
    color = models.CharField(max_length=7, default='#00a0f0')
    """ Indicates the color in hexadecimal for the service """
    color_id = models.IntegerField(default=0)
    """ Represent an index for a color array in the app """
    busStops = models.ManyToManyField(
        BusStop,
        verbose_name='Bus Stops',
        through=ServicesByBusStop)
    """ bus stops where the service stops """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        unique_together = ('service', 'gtfs')


class ServiceLocation(Location):
    """This models stores the position along the route of every bus at 20 meters apart.
    You can give the distance from the start of the travel and it return the position at that distance."""
    service = models.CharField(
        'Service Code',
        max_length=11,
        null=False,
        blank=False)  # Service code i.e. 506I or 506R
    """ Service code where the last character indicates its direction """
    distance = models.IntegerField('Route Distance')
    """ Distance traveled by the service since its origin """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        index_together = ["service", "distance"]
        unique_together = ('service', 'distance', 'gtfs')


class ServiceStopDistance(models.Model):
    """This model stores the distance for every bustop in every bus route for every service.
    Given a bus direction code xxxI or xxxR or something alike."""
    busStop = models.ForeignKey(BusStop, verbose_name='Bus Stop')
    """ Bus stops where the service is stopped """
    service = models.CharField(
        'Service Code',
        max_length=11,
        null=False,
        blank=False)  # Service code i.e. 506I or 506R
    """ It represents the Service code, ex: '506I' """
    distance = models.IntegerField('Distance Traveled')
    """ Distance traveled by the service when it reaches the bus stop """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        unique_together = ('busStop', 'service', 'gtfs')


class Route(Location):
    """ Route for each service """
    serviceCode = models.CharField(
        db_index=True,
        max_length=11,
        null=False,
        blank=False)
    """ Bus identifier """
    sequence = models.IntegerField('Sequence')
    """ point position in a route """
    gtfs = models.ForeignKey('GTFS', verbose_name='gtfs version')
    """ gtfs version """

    class Meta:
        unique_together = ('serviceCode', 'sequence', 'gtfs')
