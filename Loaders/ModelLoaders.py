# -*- coding: utf-8 -*-

import abc
import os
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

	def rowAddedMessage(self, className, rowsNum):
		return str(rowsNum) + " " + className + " rows added"

	@abc.abstractmethod
	def load(self):
		return


class BusStopLoader(Loader):
	_className = "BusStop"
	ticks = 1000

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(BusStopLoader, self).notSavedMessage("")
		return "the " + self.className + " " + data[0] +  end

	def inDBMessage(self, data):
		end = super(BusStopLoader, self).inDBMessage("")
		return "the " + self.className + " " + data[0] +  end

	def load(self):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			try:
				busStop = BusStop.objects.get_or_create(code=data[0], \
					defaults={'name': 'default', 'latitud': -100, 'longitud': -100})[0]
			except Exception, e:
				self.log.write(self.inDBMessage(data))
				self.log.write(str(e) + "\n")
				continue
			else:
				busStop.name = data[1]
				busStop.latitud = data[2]
				busStop.longitud = data[3]

			try:
				busStop.save()
			except Exception, e:
				self.log.write(self.notSavedMessage(data))
				self.log.write(str(e) + "\n")
			i+=1
			if(i%self.ticks==0):
				print super(BusStopLoader, self).rowAddedMessage(self.className, i)


class ServiceStopDistanceLoader(Loader):
	_className = "ServiceStopDistance"
	ticks = 5000

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(ServiceStopDistanceLoader, self).notSavedMessage("")
		return "The distance traveled by the service " + data[1] + " to the busStop "+ data[0] + end

	def inDBMessage(self, data):
		end = super(ServiceStopDistanceLoader, self).inDBMessage("")
		return "The distance traveled by the service " + data[1] + " to the busStop "+ data[0] + end

	def load(self):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			try:
				busStop = BusStop.objects.get(code=data[0])
				route = ServiceStopDistance.objects.get_or_create(busStop = busStop, \
					service = data[1], defaults={'distance': 0})[0]
			except Exception, e:
				self.log.write(self.inDBMessage(data))
				self.log.write(str(e) + "\n")
				continue
			else:
				route.distance = int(data[2])

			try:
				route.save()
			except Exception, e:
				self.log.write(self.notSavedMessage(data))
				self.log.write(str(e) + "\n")
			i+=1
			if(i%self.ticks==0):
				print super(ServiceStopDistanceLoader, self).rowAddedMessage(self.className, i)


class ServiceLoader(Loader):
	_className = "Service"
	ticks = 50

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(ServiceLoader, self).notSavedMessage("")
		return "The service " + data + end

	def inDBMessage(self, data):
		end = super(ServiceLoader, self).inDBMessage("")
		return "The service " + data + end

	def load(self):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			try:
				service = Service.objects.get_or_create(service = data[0], \
					defaults={'origin': 'origin', 'destiny': 'destiny'})[0]
			except Exception, e:
				self.log.write(self.inDBMessage(data[0]))
				self.log.write(str(e) + "\n")
				continue
			else:
				service.origin = data[1]
				service.destiny = data[2]
				service.color = data[3]
				service.color_id = data[4]

			try:
				service.save()
			except Exception, e:
				self.log.write(self.notSavedMessage(data[0]))
				self.log.write(str(e) + "\n")
			i+=1
			if(i%self.ticks==0):
				print super(ServiceLoader, self).rowAddedMessage(self.className, i)



class ServicesByBusStopLoader(Loader):
	_className = "ServicesByBusStop"
	ticks = 1000

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(ServicesByBusStopLoader, self).notSavedMessage("")
		return "The service " + data[1] + " for the busStop "+ data[0] + end

	def inDBMessage(self, data):
		end = super(ServicesByBusStopLoader, self).inDBMessage("")
		return "The service " + data[1] + " for the busStop "+ data[0] + end

	def load(self):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			services = data[1].split("-")
			for service in services:
				service = service.replace("\n", "")
				try:
					serviceObj = Service.objects.get(service = service[:-1])
					busStop = BusStop.objects.get(code=data[0])
					serviceByBusStop = ServicesByBusStop.objects.get_or_create(busStop = busStop, \
						service=serviceObj, defaults={'code': '000'})[0]
				except Exception, e:
					self.log.write(self.inDBMessage([data[0], service]))
					self.log.write(str(e) + "\n")
					continue
				else:
					serviceByBusStop.code = service

				try:
					serviceByBusStop.save()
				except Exception, e:
					self.log.write(self.notSavedMessage([data[0], service]))
					self.log.write(str(e) + "\n")
				i+=1
				if(i%self.ticks==0):
					print super(ServicesByBusStopLoader, self).rowAddedMessage(self.className, i)


class ServiceLocationLoader(Loader):
	_className = "ServiceLocation"
	ticks = 50000

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(ServiceLocationLoader, self).notSavedMessage("")
		return "The location of the service " + data[0] + end

	def inDBMessage(self, data):
		end = super(ServiceLocationLoader, self).inDBMessage("")
		return "The location of the service " + data[0] + end

	def load(self):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			try:
				serviceloc = ServiceLocation.objects.get_or_create(service=data[0], \
					distance = data[1], defaults={'latitud': -100, 'longitud': -100})[0]
			except Exception, e:
				self.log.write(self.inDBMessage(data))
				self.log.write(str(e) + "\n")
				continue
			else:
				serviceloc.latitud=data[2]
				serviceloc.longitud=data[3]

			try:
				serviceloc.save()
			except Exception, e:
				self.log.write(self.notSavedMessage(data))
				self.log.write(str(e) + "\n")
			i+=1
			if(i%self.ticks==0):
				print super(ServiceLocationLoader, self).rowAddedMessage(self.className, i)

class EventLoades(Loader):
	_className = "Event"
	ticks = 1000

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(EventLoades, self).notSavedMessage("")
		return "Event code " + data[0] + end

	def inDBMessage(self, data):
		end = super(EventLoades, self).inDBMessage("")
		return "Event code " + data[0] + ", update values\n"

	def load(self):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			event = Event.objects.filter(id=data[0])

			if event.exists():
				event = Event.objects.get(id=data[0])
				event.eventType = data[1]
				event.category = data[2]
				event.origin = data[3]
				event.name = data[4]
				event.description = data[5]
				event.lifespam = int(data[6])

				self.log.write(self.inDBMessage(data))		
				try:
					event.save()
				except Exception, e:
					self.log.write(self.notSavedMessage(data))
					self.log.write(str(e) + "\n")	
			else:
				Event.objects.create(id=data[0],eventType=data[1],category=data[2],\
					origin=data[3],name=data[4],description=data[5],lifespam=data[6])
			i+=1
			if(i%self.ticks==0):
				print super(EventLoades, self).rowAddedMessage(self.className, i)