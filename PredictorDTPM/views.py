from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

# python utilities
from datetime import datetime

# my stuff
from PredictorDTPM.webService.WebService import WebService
from PredictorDTPM.models import Log, BusLog
from pytz import timezone as tz

def busStopInfo(request, pSecretKey, pBusStop):
    """ return dtpm data related to buses of pBusStop """

    if settings.SECRET_KEY != pSecretKey:
        data = {'error': "You do not have permission to do this! >:(."}
        return JsonResponse(data, safe=False)

    # DTPM source
    ws = WebService(request)
    data = ws.askForServices(pBusStop)

    registerDTPMAnswer(data)

    return JsonResponse(data, safe=False)


def registerDTPMAnswer(data):
    """ register DTPM answer in database """

    local = tz(settings.TIME_ZONE)
    timestamp = local.localize(datetime.strptime("{} {}".format(data['fechaConsulta'], data['horaConsulta']),
                                                 "%Y-%m-%d %H:%M"))

    log = Log.objects.create(
        busStopCode=data['id'],
        serverTimeStamp=timezone.now(),
        dtpmTimeStamp=timestamp,
        webTransId=data['webTransId'],
        errorMessage=data['error'])

    for bus in data['servicios']:
        distance = int(bus['distancia'].replace(" mts.", "")) if bus["distancia"] is not None else None
        BusLog.objects.create(
            licensePlate=bus['patente'],
            route=bus['servicio'],
            timeMessage=bus['tiempo'],
            distance=distance,
            message=bus["msg"],
            log=log)
