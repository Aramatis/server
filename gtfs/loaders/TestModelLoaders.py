# -*- coding: utf-8 -*-
from django.utils import timezone

from gtfs.models import BusStop, ServiceStopDistance, Service, ServicesByBusStop, Route, ServiceLocation, GTFS

import abc


def deleteEndOfLine(line):
    """ delete unnecessary characteras
     \r = CR (Carriage Return) // Used as a new line character in Mac OS before X
     \n = LF (Line Feed) // Used as a new line character in Unix/Mac OS X
     \r\n = CR + LF // Used as a new line character in Window
    """
    newLine = line.replace("\r", "")
    newLine = newLine.replace("\n", "")
    return newLine


class TestLoader:
    """ Abstract class for data TestLoaders """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def className(self):
        return

    def __init__(self, csv, log, gtfsVersion):
        """ The constructor, receives a csv file with the data,
        and a log file to write the errors occurred in the process. """
        self.csv = csv
        self.log = log
        self.gtfs, _ = GTFS.objects.get_or_create(version=gtfsVersion, defaults={'timeCreation': timezone.now()})

    def rowAddedMessage(self, className, rowsNum):
        """ Return a String indicating the amount of rows added to the database. """
        return str(rowsNum) + " " + className + " rows added"

    def getErrorMessage(self, className, exception, dataName, dataValue):
        """ Return a String with a message error and the data produced the error """
        messageError = "{} -> data({}): {} | Exception: {}\n".\
            format(className, dataName, dataValue, str(exception))
        return messageError

    @abc.abstractmethod
    def load(self, filterList):
        """Read the file given and load the data in the database."""
        return


class BusStopTestLoader(TestLoader):
    """ This class load the bus stop data to the database."""
    _className = "BusStopTestLoader"
    ticks = 100000

    @property
    def className(self):
        return self._className

    def load(self, busStopCodes):
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pCode = data[0]
            pName = data[1]
            pLat = data[2]
            pLon = data[3]

            if pCode not in busStopCodes:
                continue

            try:
                BusStop.objects.create(code=pCode, gtfs=self.gtfs, name=pName,
                                       latitude=pLat, longitude=pLon)
            except Exception as e:
                dataName = "code,name,lat,lon"
                dataValue = "{};{};{};{}".format(pCode, pName, pLat, pLon)
                errorMessage = super(
                    BusStopTestLoader, self).getErrorMessage(
                    self.className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(BusStopTestLoader, self).rowAddedMessage(self.className, i)


class ServiceTestLoader(TestLoader):
    """ This class load the service data to the database."""
    _className = "ServiceTestLoader"
    ticks = 100000

    @property
    def className(self):
        return self._className

    def load(self, services):
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pServiceName = data[0]
            pOrigin = data[1]
            pDestination = data[2]
            pColor = data[3]
            pColorId = data[4]

            if pServiceName not in services:
                continue

            try:
                Service.objects.create(
                    service=pServiceName,
                    gtfs=self.gtfs,
                    origin=pOrigin,
                    destiny=pDestination,
                    color=pColor,
                    color_id=pColorId)
            except Exception as e:
                dataName = "serviceName,origin,destination,color,colorId"
                dataValue = "{};{};{};{};{}".format(
                    pServiceName, pOrigin, pDestination, pColor, pColorId)
                errorMessage = super(
                    ServiceTestLoader, self).getErrorMessage(
                    self.className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(ServiceTestLoader, self).rowAddedMessage(self.className, i)



class ServiceStopDistanceTestLoader(TestLoader):
    """ This class load the data for the ServiceStopDistance table. it needs bus stop data """
    _className = "ServiceStopDistanceTestLoader"
    ticks = 100000

    @property
    def className(self):
        return self._className

    def load(self, busStopCodes):
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pBusStopCode = data[0]
            pServiceName = data[1]
            pDistance = data[2]

            if pBusStopCode not in busStopCodes:
                continue

            try:
                busStop = BusStop.objects.get(code=pBusStopCode, gtfs=self.gtfs)
                ServiceStopDistance.objects.create(
                    busStop=busStop, gtfs=self.gtfs, service=pServiceName, distance=int(pDistance))
            except Exception as e:
                dataName = "busStopCode,serviceName,distance"
                dataValue = "{};{};{}".format(
                    pBusStopCode, pServiceName, pDistance)
                errorMessage = super(
                    ServiceStopDistanceTestLoader, self).getErrorMessage(
                    self.className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(ServiceStopDistanceTestLoader, self).rowAddedMessage(self.className, i)

class ServicesByBusStopTestLoader(TestLoader):
    """ This class load the data for the ServicesByBusStop table."""
    _className = "ServicesByBusStopTestLoader"
    ticks = 100000

    @property
    def className(self):
        return self._className

    def load(self, busStopCodes):
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pBusStopCode = data[0]
            pServices = data[1].split("-")

            if pBusStopCode not in busStopCodes:
                continue

            for pService in pServices:
                serviceWithoutDirection = pService[:-1]
                try:
                    serviceObj = Service.objects.get(
                        service=serviceWithoutDirection, gtfs=self.gtfs)
                    busStopObj = BusStop.objects.get(code=pBusStopCode, gtfs=self.gtfs)
                    ServicesByBusStop.objects.create(
                        busStop=busStopObj, gtfs=self.gtfs, service=serviceObj, code=pService)
                except Exception as e:
                    dataName = "busStopCode,ServiceNameWithDirection"
                    dataValue = "{};{}".format(pBusStopCode, pService)
                    errorMessage = super(
                        ServicesByBusStopTestLoader, self).getErrorMessage(
                        self.className, e, dataName, dataValue)
                    self.log.write(errorMessage)
                    continue

                i += 1
                if(i % self.ticks == 0):
                    print super(ServicesByBusStopTestLoader, self).rowAddedMessage(self.className, i)


class ServiceLocationTestLoader(TestLoader):
    """ This class load the data for the ServiceLocation table."""
    _className = "ServiceLocationTestLoader"
    ticks = 100000

    @property
    def className(self):
        return self._className

    def load(self, servicesWithDirection):
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pServiceName = data[0]
            pDistance = data[1]
            pLat = data[2]
            pLon = data[3]

            if pServiceName not in servicesWithDirection:
                continue

            try:
                ServiceLocation.objects.create(
                    service=pServiceName,
                    gtfs=self.gtfs,
                    distance=pDistance,
                    latitude=pLat,
                    longitude=pLon)
            except Exception as e:
                dataName = "serviceName,distance,latitude,longitude"
                dataValue = "{};{};{};{}".format(
                    pServiceName, pDistance, pLat, pLon)
                errorMessage = super(
                    ServiceLocationTestLoader, self).getErrorMessage(
                    self.className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(ServiceLocationTestLoader, self).rowAddedMessage(self.className, i)


class RouteTestLoader(TestLoader):
    """ This class load service-routes data to the database."""
    _className = "RouteTestLoader"
    ticks = 100000

    @property
    def className(self):
        return self._className

    def load(self, servicesWithDirection):
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pServiceCode = data[0]
            pLat = data[1]
            pLon = data[2]
            pSequence = data[3]

            if pServiceCode not in servicesWithDirection:
                continue

            try:
                Route.objects.create(serviceCode=pServiceCode, gtfs=self.gtfs, 
                                     latitude=pLat, longitude=pLon, sequence=pSequence)
            except Exception as e:
                dataName = "serviceCode,latitude,longitude,sequence"
                dataValue = "{};{};{};{}".format(
                    pServiceCode, pLat, pLon, pSequence)
                errorMessage = super(
                    RouteTestLoader, self).getErrorMessage(
                    self._className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(RouteTestLoader, self).rowAddedMessage(self.className, i)
