from ModelLoaders import BusStopLoader, ServiceStopDistanceLoader, ServiceLocationLoader, ServicesByBusStopLoader, ServiceLoader, RouteLoader


class LoaderFactory(object):
    """This class acts like a factory of loaders."""

    def getModelLoader(self, model):
        """It receives a string indicating the table/model where you want to save the data
        and returns the respective Loader."""

        if(model.lower() == "busstop"):
            return BusStopLoader
        elif(model.lower() == "routestopdistance"):
            return ServiceStopDistanceLoader
        elif(model.lower() == "routelocation"):
            return ServiceLocationLoader
        elif(model.lower() == "routebybusstop"):
            return ServicesByBusStopLoader
        elif(model.lower() == "route"):
            return ServiceLoader
        elif(model.lower() == "shape"):
            return RouteLoader
        else:
            return None
