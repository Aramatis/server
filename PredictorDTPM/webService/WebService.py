from suds.client import Client

# python utilities
import os
import json

# models
import PredictorDTPM.models.Log

class WebService:
    """ Communicate with TranSantiago predictor service """

    class __WebServiceClient:
        """ Singleton for suds client """

        def __init__(self):

            with open(os.path.join(os.path.dirname(__file__), 'DTPMConnectionParams.json')) as data_file:
                info = json.load(data_file)

            # WSDL url. it was gotten throught Wireless-IQ
            self.client = Client(info['wsdl'])
            # prefix for webTransId
            self.prefix = info['prefix']
            # client code to identify who is querying data
            self.clientCode = info['clientCode']
            # answer code returned for each service
            self.answerCode = info['answerCode']
            # resolution code: code, pixel size image, device resolution
            # used for makerting purposes, ignored by us
            self.resCode = info['resolutionCode']
            # transactionId
            try:
                self.transactionId = Log.objects.get().order_by('-webTransId').first().webTransId
            except:
                self.transactionId = 3000

    clientInstance = None

    __ipFinalUser = None

    def __init__(self, request):
        """ constructor """
        self.__ipFinalUser = self.__getUserIP(request)
        if not WebService.clientInstance:
            WebService.clientInstance = WebService.__WebServiceClient()

    def askForServices(self, busStop):
        """ ask for services to TranSantiago """
        client = WebService.clientInstance.client
        clientCode = WebService.clientInstance.clientCode
        resCode = WebService.clientInstance.resCode[0]['code']
        ipFinalUser = self.__ipFinalUser
        webTransId = WebService.clientInstance.prefix + \
                self.__completeId(WebService.clientInstance.transactionId)
        WebService.clientInstance.transactionId += 1

        print "WebService: \n\tclientCode:{}\n\tresolutionCode:{}\n\tipFinalUser:{},\n\twebTransId:{} "\
                .format(clientCode, resCode, ipFinalUser, webTransId)

        result = client.service.predictorParaderoServicio(
                    paradero = busStop,
                    cliente = clientCode,
                    resolucion = resCode,
                    ipUsuarioFinal = ipFinalUser,
                    webTransId = webTransId
                    )

        data = self.__parserDTPMData(result)
        return data

    def __getUserIP(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def __completeId(self, number):
        """ complete with zeros until get 20 digits """
        return str(number).zfill(20)

    def __parserDTPMData(self, dtpmInfo):
        """ separate buses. Each one in an array """

        # see the response of transantiago
        #print dtpmInfo

        response = {}
        response['fechaConsulta'] = dtpmInfo['fechaprediccion']
        response['horaConsulta'] = dtpmInfo['horaprediccion']
        response['id'] = dtpmInfo['paradero']
        response['descripcion'] = dtpmInfo['nomett']
        response['servicios'] = []
        response['error'] = None

        if (dtpmInfo['respuestaParadero'] != None):
            response['error'] = dtpmInfo['respuestaParadero']

        # for each service
        for service in dtpmInfo['servicios'][0]:
            #print service
            bus1 = {}
            bus2 = {}
            # if response is ok
            if service['codigorespuesta'] == "00":
                bus1['valido'] = 1
                bus2['valido'] = 1
            else:
                bus1['valido'] = 0
                bus2['valido'] = 0
                bus1['mensajeError'] = service['respuestaServicio']
                bus2['mensajeError'] = service['respuestaServicio']

            bus1['servicio'] = service['servicio']
            bus1['patente'] = service['ppubus1']
            bus1['tiempo'] = service['horaprediccionbus1']
            bus1['distancia'] = "{} {}".format(service['distanciabus1'], ' mts.')

            bus2['servicio'] = service['servicio']
            bus2['patente'] = service['ppubus2']
            bus2['tiempo'] = service['horaprediccionbus2']
            bus2['distancia'] = "{} {}".format(service['distanciabus2'], ' mts.')

            response['servicios'].append(bus1)
            response['servicios'].append(bus2)

        return response