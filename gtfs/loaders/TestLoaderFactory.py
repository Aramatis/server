from gtfs.loaders.TestModelLoaders import BusStopTestLoader, ServiceStopDistanceTestLoader, ServiceLocationTestLoader, \
    ServiceTestLoader, RouteTestLoader, ServicesByBusStopTestLoader


class TestLoaderFactory(object):
    """This class acts like a factory of loaders."""

    def getModelLoader(self, model):
        """It receives a string indicating the table/model where you want to save the data
        and returns the respective Loader."""

        if (model.lower() == "busstop"):
            return BusStopTestLoader
        elif (model.lower() == "servicestopdistance"):
            return ServiceStopDistanceTestLoader
        elif (model.lower() == "servicelocation"):
            return ServiceLocationTestLoader
        elif (model.lower() == "servicesbybusstop"):
            return ServicesByBusStopTestLoader
        elif (model.lower() == "service"):
            return ServiceTestLoader
        elif (model.lower() == "route"):
            return RouteTestLoader
        else:
            raise ValueError('%s is not valid model' % model)