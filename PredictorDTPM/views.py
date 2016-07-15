from django.http import JsonResponse

#python utilities
import json

# my stuff
from AndroidRequests.predictorTranSantiago.WebService import WebService

def nearbyBuses(request, pBusStop):
    """ return all information about bus stop: events and buses """

    # DTPM source
    ws = WebService(request)
    data = ws.askForServices(pBusStop)

    return JsonResponse(data, safe=False)
