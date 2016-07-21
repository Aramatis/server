# -*- coding: utf-8 -*-

import abc
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()
from AndroidRequests.models import *

class Loader:
    """ Abstract class for data loaders """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def className(self):
        return

    def __init__(self, csv, log):
        """The constructor, receives a csv file with the data,
        and a log file to write the errors occurred in the process."""
        self.csv = csv;
        self.log = log;

    def rowAddedMessage(self, className, rowsNum):
        """Return an String indicating the amount of rows added to the database."""
        return str(rowsNum) + " " + className + " rows added"

    @abc.abstractmethod
    def deleteAllRecords(self):
        """ Delete all register in database """
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
            data = line.split(";")

            if(data.count('\n')>0):
                continue

            try:
                BusStop.objects.create(code=data[0], name = data[1], \
                        latitud = data[2], longitud = data[3])
            except Exception, e:
                self.log.write(str(e) + "\n")
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
            data = line.split(";")
            if(data.count('\n')>0):
                continue

            try:
                busStop = BusStop.objects.get(code=data[0])
                route   = ServiceStopDistance.objects.create(busStop = busStop, \
                    service = data[1], distance = int(data[2]))
            except Exception, e:
                self.log.write(str(e) + "\n")
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
            data = line.split(";")
            if(data.count('\n')>0):
                continue

            try:
                Service.objects.create(service = data[0], origin = data[1], \
                        destiny = data[2], color = data[3], color_id = data[4])
            except Exception, e:
                self.log.write(str(e) + "\n")
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
            data = line.split(";")
            if(data.count('\n')>0):
                continue

            services = data[1].split("-")
            for service in services:
                service = service.replace("\n", "")
                serviceWithoutDirection = service[:-1]
                try:
                    serviceObj = Service.objects.get(service = serviceWithoutDirection)
                    busStop = BusStop.objects.get(code=data[0])
                    serviceByBusStop = ServicesByBusStop.objects.create(busStop = busStop, \
                        service=serviceObj, code = service)
                except Exception, e:
                    self.log.write(str(e) + "\n")
                    continue

                try:
                    serviceByBusStop.save()
                except Exception, e:
                    self.log.write(self.notSavedMessage([data[0], service]))
                    self.log.write(str(e) + "\n")
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
            data = line.split(";")
            if(data.count('\n')>0):
                continue

            try:
                ServiceLocation.objects.create(service=data[0], \
                    distance = data[1], latitud = data[2], longitud = data[3])
            except Exception, e:
                self.log.write(str(e) + "\n")
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
            data = line.split(";")
            if(data.count('\n')>0):
                continue

            try:
                Event.objects.create(id=data[0],eventType=data[1],category=data[2],\
                    origin=data[3],name=data[4],description=data[5],lifespam=data[6])
            except Exception, e:
                self.log.write(str(e) + "\n")
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
        Event.objects.all().delete()

    def load(self):
        self.deleteAllRecords()
        i = 1
        for line in self.csv:
            data = line.split(";")
            if(data.count('\n')>0):
                continue

            try:
                Route.objects.create(serviceCode=data[0], latitud=data[1],\
                                        longitud=data[2], sequence=data[3])
            except Exception, e:
                self.log.write(str(e) + "\n")
                continue

            i+=1
            if(i%self.ticks==0):
                print super(RouteLoader, self).rowAddedMessage(self.className, i)
