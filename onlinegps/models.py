# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class LastGPS(models.Model):
    """ keep last gps of each bus associated to transport system """
    licensePlate = models.CharField(max_length=7, db_column="patente")
    userRouteCode = models.CharField(max_length=50, db_column="servicio_usuario")
    timestamp = models.DateTimeField(db_column="tiempo")
    latitude = models.FloatField(db_column="latitud")
    longitude = models.FloatField(db_column="longitud")

    class Meta:
        indexes = [
            models.Index(fields=["licensePlate"])
        ]