from django.http import JsonResponse
from django.views.generic import View

# import DB's models
from AndroidRequests.models import Route

class ServiceRoute(View):
    """This class handles requests for a service route."""
    def __init__(self):
        self.context={}

    def get(self, request, pBusService, pLat1, pLong1, pLat2, pLong2):
        """it receive the bus Service to get points that creates service route """
        response = {}
        response['service'] = pBusService
        response['route'] = []

        # ask for the bus stops for this service
        serviceCode = pBusService + self.detectRouteDirection(pBusService, pLat1, pLong1, pLat2, pLong2)
        route = self.getRouteForService(serviceCode)

        response['route'] = route

        return JsonResponse(response, safe=False)

    def detectRouteDirection(self, pBusService, pLat1, pLong1, pLat2, pLong2):
        """ detect route direction based on two points  """
        #TODO: @fhernandez implement a criteria
        return 'I'

    def getRouteForService(self,pServiceCode):
        """ return the route defined for a service. """
        route = []

        for point in Route.objects.filter(serviceCode=pServiceCode).order_by('sequence'):
            data = {}
            data['latitude'] = point.latitud
            data['longitude'] = point.longitud
            data['sequence'] = point.sequence
            route.append(data)

        return route
