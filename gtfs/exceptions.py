
class RouteNotFoundException(Exception):
    """ error produced when service information does not exist in service table """


class RouteDistanceNotFoundException(Exception):
    """ error produced when it is not possible to get distance between a service and bus stop """


class RouteDoesNotStopInBusStop(Exception):
    """ error produced when route does not match with stop, so we can not know distance from start point """


class ThereIsNotClosestLocation(Exception):
    """ raise when there is not closest location """