from django.test import RequestFactory, Client
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

import json
import datetime as dt
import uuid

# views
from AndroidRequests.allviews.RequestTokenV2 import RequestTokenV2

from Loaders.TestLoaderFactory import TestLoaderFactory


class TestHelper():
    """ methods that help to create test cases """
    FILE_SOURCE = 'InitialData'
    GTFS_PATH = 'InitialData/{}'.format(settings.GTFS_VERSION)
    LOG_FILE_NAME = 'loadDataErrorTest.log'

    def __init__(self, testInstance):
        self.factory = RequestFactory()
        self.test = testInstance

    def __loadData(self, model, filePath, log, dataFilter=[]):
        """ load data on database """

        csv = open(filePath, 'r')  # path to csv file
        csv.next()
        factory = TestLoaderFactory()
        loader = factory.getModelLoader(model)(csv, log, settings.GTFS_VERSION)
        loader.load(dataFilter)
        csv.close()
        log.close()

    def insertEventsOnDatabase(self):
        """ loads events """

        log = open(self.LOG_FILE_NAME, 'w')
        filePath = self.FILE_SOURCE + '/events.csv'
        model = 'event' 

        self.__loadData(model, filePath, log)
 
    def insertServicesOnDatabase(self, serviceList):
        """ load services """

        log = open(self.LOG_FILE_NAME, 'w')
        filePath = self.GTFS_PATH + '/services.csv'
        model = 'service'

        self.__loadData(model, filePath, log, serviceList)

    def insertBusstopsOnDatabase(self, busStopList):
        """ load bus stops """

        log = open(self.LOG_FILE_NAME, 'w')
        filePath = self.GTFS_PATH + '/busstop.csv'
        model = 'busstop'

        self.__loadData(model, filePath, log, busStopList)

    def insertServicesByBusstopsOnDatabase(self, busStopList):
        """ load services by bus stops """

        log = open(self.LOG_FILE_NAME, 'w')
        filePath = self.GTFS_PATH + '/servicesbybusstop.csv'
        model = 'servicesbybusstop'

        self.__loadData(model, filePath, log, busStopList)

    def insertServiceStopDistanceOnDatabase(self, stopList):
        """ load service stop distance data by service with direction """

        log = open(self.LOG_FILE_NAME, 'w')
        filePath = self.GTFS_PATH + '/servicestopdistance.csv'
        model = 'servicestopdistance'

        self.__loadData(model, filePath, log, stopList)

    def insertServiceLocationOnDatabase(self, servicesWithDirection):
        """ load service location data by service with direction """

        log = open(self.LOG_FILE_NAME, 'w')
        filePath = self.GTFS_PATH + '/servicelocation.csv'
        model = 'servicelocation'

        self.__loadData(model, filePath, log, servicesWithDirection)

    def askForMachineId(self, pLicencePlate):
        """ simulate a request to get machine id based on its licence plate """
        URL = '/android/getUUID/'
        c = Client()
        URL = URL + '/'.join([pLicencePlate])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        machineId = jsonResponse['uuid']

        return machineId

    def createBusAndAssignmentOnDatabase(self, phoneId, service, licencePlate):
        """ create a bus object and assignment object """
        self.getInBusWithLicencePlate(phoneId, service, licencePlate)

    def getInBusWithLicencePlate(
            self, phoneId, service, licencePlate, time=timezone.now()):
        """ create a user on bus in database """
        machineId = self.askForMachineId(licencePlate)
        URL = '/android/requestToken/v2/'
        request = self.factory.get(URL)
        request.user = AnonymousUser()

        view = RequestTokenV2()
        response = view.get(request, phoneId, service, machineId, time)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']

        return token

    def getInBusWithMachineId(self, phoneId, service, machineId):
        """ create a user on bus in database """
        URL = '/android/requestToken/v2/'
        c = Client()
        URL = URL + '/'.join([phoneId, service, machineId])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']

        return token

    def getInBusWithLicencePlateByPost(
            self, phoneId, service, licencePlate, 
            time=timezone.now(), userId=None, sessionToken=None):
        """ create a user on bus in database """
        machineId = self.askForMachineId(licencePlate)
        URL = '/android/requestToken/v2/'
        c = Client()

        data = {}
        data['phoneId'] = phoneId
        data['busService'] = service 
        data['machineId'] = machineId
        data['userId'] = userId
        data['sessionToken'] = sessionToken

        response = c.post(URL, data)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']

        return token

    def getInBusWithMachineIdByPost(self, phoneId, service, machineId, 
            userId=None, sessionToken=None):
        """ create a user on bus in database """
        URL = '/android/requestToken/v2/'
        c = Client()

        data = {}
        data['phoneId'] = phoneId
        data['busService'] = service 
        data['machineId'] = machineId
        data['userId'] = userId
        data['sessionToken'] = sessionToken
        response = c.post(URL, data)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)
        token = jsonResponse['token']

        return token

    def endRoute(self, token):
        """ revoke token used to identify a trip """
        URL = '/android/endRoute/'
        c = Client()
        URL = URL + token
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def sendFakeTrajectoryOfToken(self, travelToken, poses=None, userId='', sessionToken=''):
        """ send fake positions for user travel """

        URL = '/android/sendTrajectory'
        request = self.factory.post(URL)
        request.user = AnonymousUser()

        now = dt.datetime.now()
        times = [now,
                 now - dt.timedelta(minutes=5),
                 now - dt.timedelta(minutes=10),
                 now - dt.timedelta(minutes=15),
                 now - dt.timedelta(minutes=20),
                 now - dt.timedelta(minutes=25),
                 now - dt.timedelta(minutes=30),
                 now - dt.timedelta(minutes=35),
                 now - dt.timedelta(minutes=40)]
        fTimes = []
        for time in times:
            fTimes.append(time.strftime("%Y-%m-%dT%X"))
        
        if poses is None:
            poses = {"poses": [
                {"latitud": -33.458771, "longitud": -70.676266,
                    "timeStamp": fTimes[0], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.458699, "longitud": -70.675708,
                    "timeStamp": fTimes[1], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.458646, "longitud": -70.674678,
                    "timeStamp": fTimes[2], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.458646, "longitud": -70.673799,
                    "timeStamp": fTimes[3], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.458413, "longitud": -70.671631,
                    "timeStamp": fTimes[4], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.457983, "longitud": -70.669035,
                    "timeStamp": fTimes[5], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.457518, "longitud": -70.666718,
                    "timeStamp": fTimes[6], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.457196, "longitud": -70.664636,
                    "timeStamp": fTimes[7], "inVehicleOrNot":"vehicle"},
                {"latitud": -33.457070, "longitud": -70.660559, "timeStamp": fTimes[8], "inVehicleOrNot":"vehicle"}]}

        c = Client()
        URL = URL
        response = c.post(URL, {'pToken': travelToken,
                                'pTrajectory': json.dumps(poses),
                                'userId': userId, 
                                'sessionToken': sessionToken})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def setDirection(self, travelKey, direction):
        """ set direction of trip """
        URL = '/android/setDirection'
        c = Client()
        URL = URL
        response = c.post(URL, {'pToken': travelKey, 'pDirection': direction})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def evaluateTrip(self, travelToken, evaluation):
        """ send trip evaluation """

        URL = '/android/evaluateTrip'
        request = self.factory.post(URL)
        request.user = AnonymousUser()

        c = Client()
        response = c.post(URL, {'token': travelToken,
                                'evaluation': evaluation})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    """
       BUS EVENT METHODS V1
    """

    def reportEvent(self, phoneId, service, licencePlate, eventCode):
        """ report an event with the old version  """
        URL = '/android/reportEventBus/'
        c = Client()
        URL = URL + \
            '/'.join([phoneId, service, licencePlate, eventCode, 'confirm'])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def confirmOrDeclineEvent(self, phoneId, service,
                              licencePlate, eventCode, confirmOrDecline):
        """ report an event with the old version  """
        URL = '/android/reportEventBus/'
        c = Client()
        URL = URL + '/'.join([phoneId, service, licencePlate,
                              eventCode, confirmOrDecline])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def requestEventsForBus(self, service, licencePlate):
        """ ask for events related to machine id """
        URL = '/android/requestEventsForBus/'
        c = Client()
        URL = URL + '/'.join([licencePlate, service])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    """
       BUS EVENT METHODS V2
    """

    def reportEventV2(self, phoneId, machineId, service, eventCode):
        """ report an event with the new version  """
        URL = '/android/reportEventBus/v2/'
        c = Client()
        URL = URL + '/'.join([phoneId, machineId, service,
                              eventCode, 'confirm'])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def confirmOrDeclineEventV2(
            self, phoneId, machineId, service, eventCode, confirmOrDecline):
        """ confirm or decline an event with the new version  """
        URL = '/android/reportEventBus/v2/'
        c = Client()
        URL = URL + '/'.join([phoneId, machineId, service,
                              eventCode, confirmOrDecline])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def requestEventsForBusV2(self, machineId):
        """ ask for events related to machine id """
        URL = '/android/requestEventsForBus/v2/'
        c = Client()
        URL = URL + '/'.join([machineId])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    """
        STOP METHODS
    """

    def reportStopEvent(self, phoneId, stopCode, eventCode, aditionalInfo = None):
        """ report an event for stop """
        URL = '/android/reportEventBusStop/'
        c = Client()
        if aditionalInfo is None:
            params = [phoneId, stopCode, eventCode, 'confirm']
        else:
            params = [phoneId, stopCode, aditionalInfo, eventCode, 'confirm']
        URL = URL + '/'.join(params)
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def confirmOrDeclineStopEvent(
            self, phoneId, stopCode, eventCode, confirmOrDecline):
        """ confirm or decline an event for stop """
        URL = '/android/reportEventBusStop/'
        c = Client()
        URL = URL + '/'.join([phoneId, stopCode, eventCode, confirmOrDecline])
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def requestEventsForBusStop(self, code):
        """ ask for events related to bus stop """
        URL = '/android/requestEventsForBusStop/'
        c = Client()
        URL = URL + code
        response = c.get(URL, {})

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse


    """
        BUS EVENT METHODS BY POST
    """
    def reportEventV2ByPost(self, phoneId, machineId, service, eventCode, userId, sessionToken):
        """ report an event with the new version  """
        URL = '/android/reportEventBus/v2'
        c = Client()
        data = {'phoneId': phoneId, 
                'machineId': machineId, 
                'service': service,
                'eventId': eventCode, 
                'vote': 'confirm', 
                'userId': userId, 
                'sessionToken': sessionToken}
        response = c.post(URL, data)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def confirmOrDeclineEventV2ByPost(
            self, phoneId, machineId, service, eventCode, confirmOrDecline, userId, sessionToken):
        """ confirm or decline an event with the new version  """
        URL = '/android/reportEventBus/v2'
        c = Client()
        data = {'phoneId': phoneId, 
                'machineId': machineId, 
                'service': service,
                'eventId': eventCode, 
                'vote': confirmOrDecline, 
                'userId': userId, 
                'sessionToken': sessionToken}
        response = c.post(URL, data)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse


    def reportStopEventByPost(self, phoneId, stopCode, eventCode, userId, sessionToken):
        """ report an event for stop """
        URL = '/android/reportEventBusStop'
        c = Client()
        data = {'phoneId': phoneId, 
                'stopCode': stopCode, 
                'eventId': eventCode, 
                'vote': 'confirm',
                'userId': userId, 
                'sessionToken': sessionToken}

        response = c.post(URL, data)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def confirmOrDeclineStopEventByPost(
            self, phoneId, stopCode, eventCode, confirmOrDecline, userId, sessionToken):
        """ confirm or decline an event for stop """
        URL = '/android/reportEventBusStop'
        c = Client()
        data = {'phoneId': phoneId, 
                'stopCode': stopCode, 
                'eventId': eventCode, 
                'vote': confirmOrDecline,
                'userId': userId, 
                'sessionToken': sessionToken}

        response = c.post(URL, data)

        self.test.assertEqual(response.status_code, 200)

        jsonResponse = json.loads(response.content)

        return jsonResponse

    def createTranSappUsers(self, userQuantity):
        ''' create @quantity users and put the user asked in @userPosition '''
        users = []

        for index in range(userNumber):
            name = "name{}".format(index)
            nickname = "nickname{}".format(index)
            userId = "userId{}".format(index)
            sessionToken = uuid.uuid4()
            phoneId = uuid.uuid4()
            user = TranSappUser.objects.create(userId=userId,
                       sessionToken=sessionToken, name=name, nickname=nickname,
                       phoneId=phoneId, accountType=TranSappUser.FACEBOOK,
                       level=self.level, globalScore=0)
            users.append(user)

        return users

