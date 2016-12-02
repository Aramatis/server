from django.http import JsonResponse
from django.views.generic import View

# import DB's models
from AndroidRequests.models import Route


class ServiceRoute(View):
    """This class handles requests for a service route."""

    def __init__(self):
        self.context = {}

    def get(self, request, pBusService, pLat1, pLon1, pLat2, pLon2):
        """it receive the bus Service to get points that creates service route """
        response = {}
        response['statusCode'] = "200"
        response['statusMessage'] = "ok"
        response['route'] = []

        # ask for the route for this service
        route = self.getRoutesForService(pBusService)

        # serviceCode = pBusService + self.detectRouteDirection(pBusService, pLat1, pLon1, pLat2, pLon2)

        response['service'] = pBusService

        if len(route) == 0:
            response['statusCode'] = "300"
            response[
                'statusMessage'] = "Service does not have route in the database."

        response['route'] = route

        return JsonResponse(response, safe=False)

    def detectRouteDirection(self, pBusService, pLat1, pLon1, pLat2, pLon2):
        """ detect route direction based on two points  """
        # TODO: @fhernandez implement a criteria
        return 'I'

    def getRoutesForService(self, pServiceCode):
        """ return the route defined for a service. """
        route = []

        service = pServiceCode + '[a-zA-Z]*'  # all variants
        service = pServiceCode + '[I,R]$'  # variant: IDA and REGRESO

        # get all services associated to number
        for service in Route.objects.values('serviceCode').filter(
                serviceCode__regex=service).distinct():
            variantCode = service['serviceCode']
            variant = {}
            variant['variant'] = variantCode
            variant['route'] = []
            for point in Route.objects.filter(
                    serviceCode=variantCode).order_by('sequence'):
                # print "{} {}".format(point.serviceCode, point.sequence)
                data = {}
                data['latitude'] = point.latitud
                data['longitude'] = point.longitud
                data['sequence'] = point.sequence
                variant['route'].append(data)
            route.append(variant)

        return route
