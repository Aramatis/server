from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from datetime import datetime

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

    registerAuthorityAnswer(data)

    return JsonResponse(data, safe=False)


def registerAuthorityAnswer(data):
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
            log=log)

    for bus in data["routeInfo"]:
        BusLog.objects.create(
            route=bus["servicio"],
            message=bus["msg"],
            log=log)