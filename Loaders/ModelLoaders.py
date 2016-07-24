# -*- coding: utf-8 -*-
import abc
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()
from AndroidRequests.models import *

def deleteEndOfLine(line):
    """ delete unnecessary characteras
     \r = CR (Carriage Return) // Used as a new line character in Mac OS before X
     \n = LF (Line Feed) // Used as a new line character in Unix/Mac OS X
     \r\n = CR + LF // Used as a new line character in Window
    """
    newLine = line.replace("\r", "")
    newLine = newLine.replace("\n", "")
    return newLine

class Loader:
    """ Abstract class for data loaders """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def className(self):
        return

    def __init__(self, csv, log):
        """ The constructor, receives a csv file with the data,
        and a log file to write the errors occurred in the process. """
        self.csv = csv;
        self.log = log;

    def rowAddedMessage(self, className, rowsNum):
        """ Return a String indicating the amount of rows added to the database. """
        return str(rowsNum) + " " + className + " rows added"

    def getErrorMessage(self, className, exception, dataName, dataValue):
        """ Return a String with a message error and the data produced the error """
        messageError = "{} -> data({}): {} | Exception: {}\n".\
                    format(self._className, dataName, dataValue, str(exception))
	return messageError

    @abc.abstractmethod
    def deleteAllRecords(self):
        """ Delete all register in database table """
        return

    @abc.abstractmethod
    def load(self):
        """Read the file given and load the data in the database."""
        return

class BusStopLoader(Loader):
    """ This class load the bus stop data to the database."""
    _className = "BusStop"
    ticks = 1000

    @property
    def className(self):
        return self._className

    def deleteAllRecords(self):
        BusStop.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
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

            try:
                BusStop.objects.create(code = pCode, name = pName, \
                        latitud = pLat, longitud = pLon)
            except Exception, e:
                dataName = "code,name,lat,lon"
                dataValue = "{};{};{};{}".format(pCode, pName, pLat, pLon)
                errorMessage = super(BusStopLoader, self).getErrorMessage(self._className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i+=1
            if(i%self.ticks==0):
                print super(BusStopLoader, self).rowAddedMessage(self.className, i)


class ServiceStopDistanceLoader(Loader):
    """ This class load the data for the ServiceStopDistance table."""
    _className = "ServiceStopDistance"
    ticks = 5000

    @property
    def className(self):
        return self._className

    def deleteAllRecords(self):
        ServiceStopDistance.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pBusStopCode = data[0]
            pServiceName = data[1]
            pDistance = data[2]
            try:
                busStop = BusStop.objects.get(code = pBusStopCode)
                route   = ServiceStopDistance.objects.create(busStop = busStop, \
                    service = pServiceName, distance = int(pDistance))
            except Exception, e:
                dataName = "busStopCode,serviceName,distance"
                dataValue = "{};{};{}".format(pBusStopCode, pServiceName, pDistance)
                errorMessage = super(ServiceStopDistanceLoader, self).getErrorMessage(self._className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i+=1
            if(i%self.ticks==0):
                print super(ServiceStopDistanceLoader, self).rowAddedMessage(self.className, i)


class ServiceLoader(Loader):
    """ This class load the service data to the database."""
    _className = "Service"
    ticks = 50

    @property
    def className(self):
        return self._className

    def deleteAllRecords(self):
        Service.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
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

            try:
                Service.objects.create(service = pServiceName, origin = pOrigin, \
                        destiny = pDestination, color = pColor, color_id = pColorId)
            except Exception, e:
                dataName = "serviceName,origin,destination,color,colorId"
                dataValue = "{};{};{};{};{}".format(pServiceName, pOrigin, pDestination, pColor, pColorId)
                errorMessage = super(ServiceLoader, self).getErrorMessage(self._className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i+=1
            if(i%self.ticks==0):
                print super(ServiceLoader, self).rowAddedMessage(self.className, i)

class ServicesByBusStopLoader(Loader):
    """ This class load the data for the ServicesByBusStop table."""
    _className = "ServicesByBusStop"
    ticks = 1000

    @property
    def className(self):
        return self._className

    def deleteAllRecords(self):
        ServicesByBusStop.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pBusStopCode = data[0]
            pServices = data[1].split("-")
            for pService in pServices:
                serviceWithoutDirection = pService[:-1]
                try:
                    serviceObj = Service.objects.get(service = serviceWithoutDirection)
                    busStopObj = BusStop.objects.get(code = pBusStopCode)
                    ServicesByBusStop.objects.create(busStop = busStopObj, service = serviceObj, code = pService)
                except Exception, e:
                    dataName = "busStopCode,ServiceNameWithDirection"
                    dataValue = "{};{}".format(pBusStopCode, pService)
                    errorMessage = super(ServicesByBusStopLoader, self).getErrorMessage(self._className, e, dataName, dataValue)
                    self.log.write(errorMessage)
                    continue

                i+=1
                if(i%self.ticks==0):
                    print super(ServicesByBusStopLoader, self).rowAddedMessage(self.className, i)


class ServiceLocationLoader(Loader):
    """ This class load the data for the ServiceLocation table."""
    _className = "ServiceLocation"
    ticks = 50000

    @property
    def className(self):
        return self._className

    def deleteAllRecords(self):
        ServiceLocation.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
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
            try:
                ServiceLocation.objects.create(service = pServiceName, \
                    distance = pDistance, latitud = pLat, longitud = pLon)
            except Exception, e:
                dataName = "serviceName,distance,latitude,longitude"
                dataValue = "{};{};{};{}".format(pServiceName, pDistance, pLat, pLon)
                errorMessage = super(ServiceLocationLoader, self).getErrorMessage(self._className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i+=1
            if(i%self.ticks==0):
                print super(ServiceLocationLoader, self).rowAddedMessage(self.className, i)

class EventLoader(Loader):
    """ This class load the events data to the database."""
    _className = "Event"
    ticks = 1

    @property
    def className(self):
        return self._className

    def deleteAllRecords(self):
        Event.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
        i = 1
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pId = data[0]
            pEventType = data[1]
            pCategory = data[2]
            pOrigin = data[3]
            pName = data[4]
            pDescription = data[5]
            pLifespam = data[6]
            try:
                Event.objects.create(id = pId, eventType = pEventType, category = pCategory,\
                    origin = pOrigin, name = pName, description = pDescription, lifespam = pLifespam)
            except Exception, e:
                dataName = "id,eventType,category,origin,name,description,lifespam"
                dataValue = "{};{};{};{};{};{};{}".format(pId, pEventType, pCategory, pOrigin, pName, pDescription, pLifespam)
                errorMessage = super(EventLoader, self).getErrorMessage(self._className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i+=1
            if(i%self.ticks==0):
                print super(EventLoader, self).rowAddedMessage(self.className, i)

class RouteLoader(Loader):
    """ This class load service-routes data to the database."""
    _className = "Route"
    ticks = 30000

    @property
    def className(self):
        return self._className

    def deleteAllRecords(self):
        Route.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
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
            try:
                Route.objects.create(serviceCode = pServiceCode, latitud = pLat,\
                                        longitud = pLon, sequence = pSequence)
            except Exception, e:
                dataName = "serviceCode,latitude,longitude,sequence"
                dataValue = "{};{};{};{}".format(pServiceCode, pLat, pLon, pSequence)
                errorMessage = super(RouteLoader, self).getErrorMessage(self._className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i+=1
            if(i%self.ticks==0):
                print super(RouteLoader, self).rowAddedMessage(self.className, i)
