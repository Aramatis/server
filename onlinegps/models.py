# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class LastGPS(models.Model):
    """ keep last gps of each bus associated to transport system """
    licensePlate = models.CharField(max_length=7, db_column="patente")
    authRouteCode = models.CharField(max_length=50, db_column="servicio")
    userRouteCode = models.CharField(max_length=50, db_column="servicio_usuario")
    timestamp = models.DateTimeField(db_column="tiempo")
    longitude = models.FloatField(db_column="longitud")
    latitude = models.FloatField(db_column="latitud")
    xUTM = models.IntegerField(db_column="x")
    yUTM = models.IntegerField(db_column="y")
    distanceOnPath = models.IntegerField(db_column="dist_en_ruta")
    distanceToPath = models.IntegerField(db_column="dist_a_ruta")
    speed = models.IntegerField(db_column="velocidad")
    speedWith2GPS = models.IntegerField(db_column="velocidad_2gps")
    speedWith4GPS = models.IntegerField(db_column="velocidad_4gps")
    operator = models.IntegerField(db_column="operador")
    orientation = models.IntegerField(db_column="orientacion")
    orientationAngle = models.IntegerField(db_column="orientacion_angulo")
    type = models.CharField(max_length=10, db_column="tipo")
    # characteristic of the bus machine
    busCapacity = models.IntegerField(db_column="capacidad")
    timeToPreviousBus = models.IntegerField(db_column="tiempo_sgt_bus")
    detention = models.IntegerField(db_column="detencion")