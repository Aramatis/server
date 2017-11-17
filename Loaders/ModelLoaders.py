# -*- coding: utf-8 -*-
import abc
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()
from AndroidRequests.models import BusStop, ServiceStopDistance, Service, ServicesByBusStop, Event, Route, ServiceLocation, GTFS
from django.utils import timezone


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
        msgException = str(exception)
        msgException = msgException.replace('\n', '')
        messageError = "=========================================\n"\
                       "Exception: {}\n"\
                       "Loader: {}\n"\
                       "Data columns: {}\n"\
                       "Values: {}"\
                       "=========================================\n".\
            format(msgException, className, dataName, dataValue)
        return messageError

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

    def load(self):
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
                BusStop.objects.get_or_create(code=pCode, gtfs=self.gtfs, 
                                              defaults={'name': pName,
                                                        'latitude': pLat, 
                                                        'longitude': pLon})
            except Exception as e:
                dataName = "code,name,lat,lon"
                dataValue = "{};{};{};{}\n".format(pCode, pName, pLat, pLon)
                errorMessage = super(
                    BusStopLoader, self).getErrorMessage(
                    self.className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(BusStopLoader, self).rowAddedMessage(self.className, i)


class ServiceLoader(Loader):
    """ This class load the service data to the database."""
    _className = "Service"
    ticks = 50

    @property
    def className(self):
        return self._className

    def load(self):
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
                Service.objects.get_or_create(service=pServiceName,gtfs=self.gtfs,
                        defaults={'origin':pOrigin, 'destiny':pDestination,
                                  'color':pColor, 'color_id':pColorId})
            except Exception as e:
                dataName = "serviceName,origin,destination,color,colorId"
                dataValue = "{};{};{};{};{}\n".format(
                    pServiceName, pOrigin, pDestination, pColor, pColorId)
                errorMessage = super(
                    ServiceLoader, self).getErrorMessage(
                    self.className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(ServiceLoader, self).rowAddedMessage(self.className, i)


class ServiceStopDistanceLoader(Loader):
    """ This class load the data for the ServiceStopDistance table. 
    It assumes bustops data exist in database """
    _className = "ServiceStopDistance"
    ticks = 5000

    @property
    def className(self):
        return self._className

    def load(self):
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
                busStop = BusStop.objects.get(code=pBusStopCode, gtfs=self.gtfs)
                ServiceStopDistance.objects.get_or_create(busStop=busStop, service=pServiceName, gtfs=self.gtfs, 
                        defaults={'distance':int(pDistance)})
            except Exception as e:
                dataName = "busStopCode,serviceName,distance"
                dataValue = "{};{};{}\n".format(
                    pBusStopCode, pServiceName, pDistance)
                errorMessage = super(
                    ServiceStopDistanceLoader, self).getErrorMessage(
                    self.className, e, dataName, dataValue)
                self.log.write(errorMessage)
                continue

            i += 1
            if(i % self.ticks == 0):
                print super(ServiceStopDistanceLoader, self).rowAddedMessage(self.className, i)


class ServicesByBusStopLoader(Loader):
    """ This class load the data for the ServicesByBusStop table."""
    _className = "ServicesByBusStop"
    ticks = 1000

    @property
    def className(self):
        return self._className

    def processData(self, rows, index):
        try:
            ServicesByBusStop.objects.bulk_create(rows)
            print super(ServicesByBusStopLoader, self).rowAddedMessage(self.className, index)
        except Exception as e:
            dataName = "busStopCode,ServiceNameWithDirection"
            dataValue = ""
            for row in rows:
                dataValue = dataValue + "{};{}\n".format(
                    row.busStop.code, row.code)
            errorMessage = super(
                ServicesByBusStopLoader, self).getErrorMessage(
                self.className, e, dataName, dataValue)
            self.log.write(errorMessage)
            print "{}: Error in bulk_create [{},{}]".format(self._className, index-self.ticks, index)

    def load(self):
        i = 0

        rows = []
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
                    serviceObj = Service.objects.get(
                        service=serviceWithoutDirection, gtfs=self.gtfs)
                    busStopObj = BusStop.objects.get(code=pBusStopCode, gtfs=self.gtfs)
                    row = ServicesByBusStop(
                        busStop=busStopObj, gtfs=self.gtfs, service=serviceObj, code=pService)
                    rows.append(row)
                except Exception as e:
                    dataName = "busStopCode,ServiceNameWithDirection"
                    dataValue = "{};{}\n".format(pBusStopCode, pService)
                    errorMessage = super(
                        ServicesByBusStopLoader, self).getErrorMessage(
                        self.className, e, dataName, dataValue)
                    self.log.write(errorMessage)
                    continue

                i += 1
                if(i % self.ticks == 0):
                    self.processData(rows, i)
                    rows = []

        if len(rows) > 0:
            self.processData(rows, i)


class ServiceLocationLoader(Loader):
    """ This class load the data for the ServiceLocation table."""
    _className = "ServiceLocation"
    ticks = 1000

    @property
    def className(self):
        return self._className

    def processData(self, rows, index):
        try:
            ServiceLocation.objects.bulk_create(rows)
            print super(ServiceLocationLoader, self).rowAddedMessage(self.className, index)
        except Exception as e:
            dataName = "serviceName,distance,latitude,longitude"
            dataValue = ""
            for row in rows:
                dataValue = dataValue + "{};{};{};{}\n".format(
                    row.service, row.distance, row.latitude, row.longitude)
            errorMessage = super(
                ServiceLocationLoader, self).getErrorMessage(
                self.className, e, dataName, dataValue)
            self.log.write(errorMessage)
            print "{}: Error in bulk_create [{},{}]".format(self._className, index-self.ticks, index)

    def load(self):
        i = 0

        rows = []
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pServiceName = data[0]
            pDistance = data[1]
            pLat = data[2]
            pLon = data[3]

            row = ServiceLocation(
                service=pServiceName,
                distance=pDistance,
                latitude=pLat,
                longitude=pLon,
                gtfs=self.gtfs)
            rows.append(row)

            i += 1
            if(i % self.ticks == 0):
                self.processData(rows, i)
                rows = []

        if len(rows) > 0:
            self.processData(rows, i)


class RouteLoader(Loader):
    """ This class load service-routes data to the database."""
    _className = "Route"
    ticks = 1000

    @property
    def className(self):
        return self._className

    def processData(self, rows, index):
        try:
            Route.objects.bulk_create(rows)
            print super(RouteLoader, self).rowAddedMessage(self.className, index)
        except Exception as e:
            dataName = "serviceCode,latitude,longitude,sequence"
            dataValue = ""
            for row in rows:
                dataValue = dataValue + "{};{};{};{}\n".format(
                    row.serviceCode, row.latitude, row.longitude, row.sequence)
            errorMessage = super(
                RouteLoader, self).getErrorMessage(
                self.className, e, dataName, dataValue)
            self.log.write(errorMessage)
            print "{}: Error in bulk_create [{},{}]".format(self._className, index-self.ticks, index)

    def load(self):
        i = 0

        rows = []
        for line in self.csv:
            line = deleteEndOfLine(line)
            if len(line) == 0:
                continue

            data = line.split(";")

            pServiceCode = data[0]
            pLat = data[1]
            pLon = data[2]
            pSequence = data[3]
            
            row = Route(serviceCode=pServiceCode, latitude=pLat,
                        longitude=pLon, sequence=pSequence, gtfs=self.gtfs)
            rows.append(row)

            i += 1
            if(i % self.ticks == 0):
                self.processData(rows, i)
                rows = []

        if len(rows) > 0:
            self.processData(rows, i)

