# -*- coding: utf-8 -*-

import abc
import os
from Loader import Loader
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()
from AndroidRequests.models import *

class Loader:
	
	__metaclass__ = abc.ABCMeta

	@abc.abstractproperty
	def className(self):
		return

	def __init__(self, csv, log):
		self.csv = csv;
		self.log = log;

	@abc.abstractmethod
	def notSavedMessage(self, data):
		return " couldn't be saved\n"

	@abc.abstractmethod
	def inDBMessage(self, data):
		return " is already in the DB\n"

	def rowAddedMessage(className, rowsNum):
		return str(rowsNum) + " " + className + " rows added"

	@abc.abstractmethod
	def load(self, ticks):
		return


class BusStopLoader(Loader):
	_className = "BusStop"

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(BusStopLoader, self).notSavedMessage("")
		return "the " + self.className + " " + data[0] +  end

	def inDBMessage(self, data):
		end = super(BusStopLoader, self).inDBMessage("")
		return "the " + self.className + " " + data[0] +  end

	def load(self, ticks):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			try:
				bustop = BusStop.objects.get_or_create(code=data[0], name = data[1], \
					latitud = data[2], longitud = data[3])[0]
			except Exception, e:
				self.log.write(self.inDBMessage(data))
				self.log.write(str(e) + "\n")
				continue

			try:
				bustop.save()
			except Exception, e:
				self.log.write(self.notSavedMessage(data))
				self.log.write(str(e) + "\n")
			i+=1
			if(i%ticks==0):
				print super(BusStopLoader, self).rowAddedMessage(self.className, i)


class ServiceStopDistanceLoader(Loader):
	_className = "ServiceStopDistance"

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(ServiceStopDistanceLoader, self).notSavedMessage("")
		return "The distance traveled by the service " + data[1] + " to the busStop "+ data[0] + end

	def inDBMessage(self, data):
		end = super(ServiceStopDistanceLoader, self).inDBMessage("")
		return "The distance traveled by the service " + data[1] + " to the busStop "+ data[0] + end

	def load(self, ticks):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			try:
				busstop = BusStop.objects.get(code=data[0])
				route = ServiceStopDistance.objects.get_or_create(busStop = busstop, \
					service = data[1], distance=data[2])[0]
			except Exception, e:
				self.log.write(self.inDBMessage(data))
				self.log.write(str(e) + "\n")
				continue

			try:
				route.save()
			except Exception, e:
				self.log.write(self.notSavedMessage(data))
				self.log.write(str(e) + "\n")
			i+=1
			if(i%ticks==0):
				print super(ServiceStopDistanceLoader, self).rowAddedMessage(self.className, i)


class ServiceLocationLoader(Loader):
	_className = "ServiceLocation"

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(ServiceLocationLoader, self).notSavedMessage("")
		return "The location of the service " + data[0] + end

	def inDBMessage(self, data):
		end = super(ServiceLocationLoader, self).inDBMessage("")
		return "The location of the service " + data[0] + end

	def load(self, ticks):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			try:
				serviceloc = ServiceLocation.objects.get_or_create(service=data[0], \
					distance = data[1], latitud=data[2], longitud=data[3])[0]
			except Exception, e:
				self.log.write(self.inDBMessage(data))
				self.log.write(str(e) + "\n")
				continue

			try:
				serviceloc.save()
			except Exception, e:
				self.log.write(self.notSavedMessage(data))
				self.log.write(str(e) + "\n")
			i+=1
			if(i%ticks==0):
				print super(ServiceLocationLoader, self).rowAddedMessage(self.className, i)