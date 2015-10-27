from ModelLoaders import *
class LoaderFactory():

	def getModelLoader(self, model):
		if(model.lower()=="busstop"):
			return BusStopLoader
		elif(model.lower()=="servicestopdistance"):
			return ServiceStopDistanceLoader
		elif(model=="servicelocation"):
			return ServiceLocationLoader
		else:
			return None