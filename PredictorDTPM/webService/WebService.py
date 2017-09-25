from suds.client import Client

# python utilities
import os
import json

# models
from PredictorDTPM.models import Log


class WebService:
    """ Communicate with TranSantiago predictor service """

    class WebServiceClient:
        """ Singleton for suds client """

        def __init__(self):

            with open(os.path.join(os.path.dirname(__file__), 
                    "../../server/keys/DTPMConnectionParams.json")) as data_file:
                info = json.load(data_file)

            # WSDL url. it was gotten throught Wireless-IQ
            self.client = Client(info["wsdl"])
            # prefix for webTransId
            self.prefix = info["prefix"]
            # client code to identify who is querying data
            self.clientCode = info["clientCode"]
            # answer code returned for each service
            self.answerCode = info["answerCode"]
            # resolution code: code, pixel size image, device resolution
            # used for makerting purposes, ignored by us
            self.resCode = info["resolutionCode"]
            # transactionId
            try:
                webTransId = Log.objects.order_by("-webTransId").first().webTransId
                webTransId = int(webTransId.replace(self.prefix, "")) + 1
            except:
                webTransId = 2600

            self.transactionId = webTransId

    clientInstance = None

    __ipFinalUser = None

    def __init__(self, request):
        """ constructor """
        self.__ipFinalUser = self.__getUserIP(request)
        if WebService.clientInstance is None:
            WebService.clientInstance = WebService.WebServiceClient()

    def askForServices(self, busStop):
        """ ask for services to TranSantiago """
        client = WebService.clientInstance.client
        clientCode = WebService.clientInstance.clientCode
        resCode = WebService.clientInstance.resCode[0]["code"]
        ipFinalUser = self.__ipFinalUser
        webTransId = WebService.clientInstance.prefix + \
                self.__completeId(WebService.clientInstance.transactionId)
        WebService.clientInstance.transactionId += 1

        # print "WebService: \n\tclientCode:{}\n\tresolutionCode:{}\n\tipFinalUser:{},\n\twebTransId:{} "\
        #        .format(clientCode, resCode, ipFinalUser, webTransId)

        result = client.service.predictorParaderoServicio(
                    paradero=busStop,
                    cliente=clientCode,
                    resolucion=resCode,
                    ipUsuarioFinal=ipFinalUser,
                    webTransId=webTransId
                    )

        data = self.__parserDTPMData(result)

        # add web trans id to log in database
        data["webTransId"] = webTransId

        return data

    def __getUserIP(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def __completeId(self, number):
        """ complete with zeros until get 20 digits """
        return str(number).zfill(20)

    def __parserDTPMData(self, dtpmInfo):
        """ separate buses. Each one in an array """

        response = {
            "fechaConsulta": dtpmInfo["fechaprediccion"],
            "horaConsulta": dtpmInfo["horaprediccion"],
            "id": dtpmInfo["paradero"],
            "descripcion": dtpmInfo["nomett"],
            "servicios": [],
            "error": None
        }

        if (dtpmInfo["respuestaParadero"] is not None):
            response["error"] = dtpmInfo["respuestaParadero"]

        # for each route
        for route in dtpmInfo["servicios"][0]:
            bus_list = []
            bus1 = {
                "servicio": None,
                "patente": None,
                "tiempo": None,
                "distancia": None,
                "msg": None,
                "valido": 1
            }

            # information about next two buses
            if route["codigorespuesta"] == "00":

                bus1["servicio"] = route["servicio"].strip()
                bus1["patente"] = route["ppubus1"].replace("-", "").strip().upper()
                bus1["tiempo"] = route["horaprediccionbus1"]
                bus1["distancia"] = "{} {}".format(route["distanciabus1"], " mts.")

                bus2 = {
                    "servicio": route["servicio"].strip(),
                    "patente": route["ppubus2"].replace("-", "").strip().upper(),
                    "tiempo": route["horaprediccionbus2"],
                    "distancia": "{} {}".format(route["distanciabus2"], " mts."),
                    "msg": None,
                    "valido": 1
                }

                bus_list.append(bus1)
                bus_list.append(bus2)

            # information about next bus
            elif route["codigorespuesta"] == "01":

                bus1["servicio"] = route["servicio"].strip()
                bus1["patente"] = route["ppubus1"].replace("-", "").strip().upper()
                bus1["tiempo"] = route["horaprediccionbus1"]
                bus1["distancia"] = "{} {}".format(route["distanciabus1"], " mts.")

                bus_list.append(bus1)

            # 09: information about frequency
            # 10: there is not buses to bus stop
            # 11: route out of schedule
            # 12: route not available
            elif route["codigorespuesta"] in ["09", "10", "11", "12"]:
                bus1["servicio"] = route["servicio"].strip()
                bus1["msg"] = route["respuestaServicio"]

                bus_list.append(bus1)

            # 14: stop does not math with route asked
            # 20: system error. it"s catch by stop error
            # 21: invalid query
            # 23: invalid stop
            # 24: invalid route. It is used when ask for route and stop, not our case
            elif route["codigorespuesta"] in ["14", "20", "21", "23", "24"]:
                print("proccessing route from authority predictor: ", route["respuestaServicio"])

            response["servicios"] += bus_list

        return response
