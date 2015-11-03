from ModelLoaders import *
class LoaderFactory():

	def getModelLoader(self, model):
		if(model.lower()=="busstop"):
			return BusStopLoader
		elif(model.lower()=="servicestopdistance"):
			return ServiceStopDistanceLoader
		elif(model.lower()=="servicelocation"):
			return ServiceLocationLoader
		elif(model.lower()=="servicesbybusstop"):
			return ServicesByBusStopLoader
		else:
			return None