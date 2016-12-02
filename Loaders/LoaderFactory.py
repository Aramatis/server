from ModelLoaders import BusStopLoader, ServiceStopDistanceLoader, ServiceLocationLoader, ServicesByBusStopLoader, ServiceLoader, EventLoader, RouteLoader


class LoaderFactory():
    """This class acts like a factory of loaders."""

    def getModelLoader(self, model):
        """It receives a string indicating the table/model where you want to save the data
        and returns the respective Loader."""

        if(model.lower() == "busstop"):
            return BusStopLoader
        elif(model.lower() == "servicestopdistance"):
            return ServiceStopDistanceLoader
        elif(model.lower() == "servicelocation"):
            return ServiceLocationLoader
        elif(model.lower() == "servicesbybusstop"):
            return ServicesByBusStopLoader
        elif(model.lower() == "service"):
            return ServiceLoader
        elif(model.lower() == "event"):
            return EventLoader
        elif(model.lower() == "route"):
            return RouteLoader
        else:
            return None
