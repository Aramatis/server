from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

#python utilities
import json
from datetime import datetime

# my stuff
from PredictorDTPM.webService.WebService import WebService
from PredictorDTPM.models import Log, BusLog

def busStopInfo(request, pSecretKey, pBusStop):
    """ return dtpm data related to buses of pBusStop """

    if settings.SECRET_KEY != pSecretKey:
        data = {}
        data['error'] = "You do not have permission to do this! >:(."
        return JsonResponse(data, safe=False)

    # DTPM source
    ws = WebService(request)
    data = ws.askForServices(pBusStop)

    registerDTPMAnswer(data)

    return JsonResponse(data, safe=False)

def registerDTPMAnswer(data):
    """ register DTPM answer in database """
    ignoreBuses = False
    if data['error'] != '':
        ignoreBuses = True

    log = Log.objects.create(\
            busStopCode = data['id'], \
            serverTimeStamp = timezone.now(),\
            dtpmTimeStamp = datetime.strptime(\
                "{} {}".format(data['fechaConsulta'], data['horaConsulta']), "%Y-%m-%d %H:%M"),\
            webTransId = data['webTransId'], \
            errorMessage = data['error'])

    if not ignoreBuses:
        for bus in data['servicios']:
            distance = int(bus['distancia'].replace(" mts.", ""))
            BusLog.objects.create(\
                    licensePlate = bus['patente'], \
                    serviceName = bus['servicio'], \
                    timeMessage = bus['tiempo'], \
                    distance = distance, \
                    valid = bus['valido'], \
                    log = log)



