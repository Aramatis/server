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


class ServicesByBusStopLoader(Loader):
	_className = "ServicesByBusStop"

	@property
	def className(self):
		return self._className

	def notSavedMessage(self, data):
		end = super(ServicesByBusStopLoader, self).notSavedMessage("")
		return "The service " + data[1] + " for the busStop "+ data[0] + end

	def inDBMessage(self, data):
		end = super(ServicesByBusStopLoader, self).inDBMessage("")
		return "The service " + data[1] + " for the busStop "+ data[0] + end

	def load(self, ticks):
		i = 1
		for line in self.csv:
			data = line.split(";")
			if(data.count('\n')>0):
				continue
			services = data[1].split("-")
			for service in services:
				try:
					busstop = BusStop.objects.get(code=data[0])
					serviceByBusStop = ServicesByBusStop.objects.get_or_create(busStop = busstop, \
						code=service, service = service[:-1])[0]
				except Exception, e:
					self.log.write(self.inDBMessage([data[0], service]))
					self.log.write(str(e) + "\n")
					continue

				try:
					serviceByBusStop.save()
				except Exception, e:
					self.log.write(self.notSavedMessage([data[0], service]))
					self.log.write(str(e) + "\n")
				i+=1
				if(i%ticks==0):
					print super(ServicesByBusStopLoader, self).rowAddedMessage(self.className, i)


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

class LoadEvents(object):

	def loadEvents(self):
		#Events for the bustop, the 5 digit of the id are in hexadecimal
		# Events for bunching
		Event.objects.get_or_create(id ='evn00000', name='2 juntos', description='Dos buses del mismo servicio pasan juntos por la misma parada.',\
			lifespam=30, category='buses Juntos', origin='o', eventType='busStop')
		Event.objects.get_or_create(id ='evn00001', name='3 o + juntos', description='Más de dos busesdel mismo servicio pasan juntos por la misma parada.',\
			lifespam=30, category='buses Juntos', origin='o', eventType='busStop')
		# Events for estado fisico
		Event.objects.get_or_create(id ='evn00010', name='No hay techo', description='Al paradero le falta el techo completo o parte de él.',\
			lifespam=43200, category='estado físico', origin='o', eventType='busStop')
		Event.objects.get_or_create(id ='evn00011', name='No hay asientos', description='En el paradero no existe un lugar adecuado para sentarse',\
			lifespam=43200, category='estado físico', origin='o', eventType='busStop')
		Event.objects.get_or_create(id ='evn00012', name='No hay iluminación', description='En el paradero no hay luces que lo iliminen.',\
			lifespam=43200, category='estado físico', origin='o', eventType='busStop')
		Event.objects.get_or_create(id ='evn00013', name='Falta informacion recorridos.', description='En el paradero no se especifica que servicios pasan por ahi.',\
			lifespam=43200, category='estado físico', origin='o', eventType='busStop')
		# Events for Robos o desordenes
		Event.objects.get_or_create(id ='evn00020', name='Robos o desordenes', description='En el paradero se precencias robos o se han producido disturbios',\
			lifespam=5, category='ambiente', origin='o', eventType='busStop')
		Event.objects.get_or_create(id ='evn00021', name='Ebrio', description='Hay personas ebrais en el paradero',\
			lifespam=5, category='ambiente', origin='o', eventType='busStop')
		Event.objects.get_or_create(id ='evn00022', name='Paradero lleno', description='El paradero esta repleto',\
			lifespam=5, category='ambiente', origin='o', eventType='busStop')

		#Events for the bus reported from the busStop
		Event.objects.get_or_create(id ='evn00100', name='Bus en transito', description='El bus que estaba informado para pasar por el paradero paso en transito.',\
			lifespam=3000, category='desde paradero', origin='o', eventType='bus')
		Event.objects.get_or_create(id ='evn00101', name='Bus vacio no se detuvo', description='El bus estaba vacio o casi vacio de pasajeros y no paro en el paradero.',\
			lifespam=3000, category='desde paradero', origin='o', eventType='bus')
		Event.objects.get_or_create(id ='evn00102', name='Bus lleno no se detuvo', description='El bus estaba lleno de pasajeros y no paro en el paradero.',\
			lifespam=3000, category='desde parader0', origin='o', eventType='bus')

		#Events for the bus
		# Event for ambiente
		Event.objects.get_or_create(id ='evn00200', name='Imposible moverse', description='No se puede transitar por el bus, dada la cantidad de gente.',\
			lifespam=5, category='ambiente', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00201', name='Se puede caminar con dificultad', description='El bus esta lleno y es dificil circular por él.',\
			lifespam=5, category='ambiente', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00202', name='No hay asientos disponibles', description='No se puede serntar en ningun asiento.',\
			lifespam=5, category='ambiente', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00203', name='Hay asientos disponibles', description='El bus tiene asientos libres.',\
			lifespam=5, category='ambiente', origin='i', eventType='bus')
		# Event for indidentes en el bus
		Event.objects.get_or_create(id ='evn00210', name='Están Robando', description='En el bus se presencio un robo.',\
			lifespam=5, category='incidentes en el bus', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00211', name='Están Bebiendo', description='El bus hay pasajero(s) bebiendo.',\
			lifespam=5, category='incidentes en el bus', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00212', name='Grupo haciendo desorden', description='Hay gente haciendo desorden al interior del bus.',\
			lifespam=5, category='incidentes en el bus', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00213', name='Todo tranquilo', description='El bus esta bien.',\
			lifespam=5, category='incidentes en el bus', origin='i', eventType='bus')
		# Event for estado físico del bus
		Event.objects.get_or_create(id ='evn00220', name='Puerta en mal estado', description='El bus tiene al menos una puerta en mal estado.',\
			lifespam=3000, category='estado físico', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00221', name='Pasamanos en mal estado', description='El bus tiene al menos un pasamanos en mal estado.',\
			lifespam=3000, category='estado físico', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00222', name='Ventana en mal estado', description='El bus tiene al menos una ventana en mal estado.',\
			lifespam=3000, category='estado físico', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00223', name='Timbre en mal estado', description='El bus tiene al menos un timbre en mal estado.',\
			lifespam=3000, category='estado físico', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00224', name='Sucio', description='El bus esta sucio.',\
			lifespam=3000, category='estado físico', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00225', name='Bus en buen estado', description='El bus esta en buenas condiciones para funcionar.',\
			lifespam=3000, category='estado físico', origin='i', eventType='bus')
		# Event for conductor
		Event.objects.get_or_create(id ='evn00230', name='conducción brusca', description='El chofer raliza maniobras que hacer peligrar mi bien estar.',\
			lifespam=30, category='conductor', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00231', name='no para en parader', description='El bus no paro en el paradero, pese a que alguien pidio la parada desde el bus o el paradero.',\
			lifespam=30, category='conductor', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00232', name='habla por celular', description='El chofer hable por celular mientras maneja.',\
			lifespam=5, category='conductor', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00233', name='buen comportamiento', description='El bus va bien.',\
			lifespam=5, category='conductor', origin='i', eventType='bus')
		# Event for incidente en la via
		Event.objects.get_or_create(id ='evn00240', name='taco', description='El bus esta en un taco.',\
			lifespam=5, category='incidente en la via', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00241', name='accidente', description='El bus paso cerca de un accidente.',\
			lifespam=5, category='incidente en la via', origin='i', eventType='bus')
		Event.objects.get_or_create(id ='evn00242', name='sin novedad', description='El bus va bien.',\
			lifespam=5, category='incidente en la via', origin='i', eventType='bus')
		
