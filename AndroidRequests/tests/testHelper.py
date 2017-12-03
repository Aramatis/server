from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, Client
from django.utils import timezone

from AndroidRequests.allviews.RequestTokenV2 import RequestTokenV2
from AndroidRequests.models import TranSappUser, Level, EventRegistration
from AndroidRequests.encoder import TranSappJSONEncoder
from gtfs.loaders.TestLoaderFactory import TestLoaderFactory

import json
import uuid
import os
import random


class TestHelper:
    """ methods that help to create test cases """
    GTFS_PATH = os.path.join(settings.BASE_DIR, 'gtfs', 'data', settings.GTFS_VERSION, 'server')
    LOG_FILE_NAME = 'loadDataErrorTest.log'

    def __init__(self, test_instance):
        self.factory = RequestFactory()
        self.test = test_instance

    def __load_data(self, model, file_path, log, data_filter=None):
        """ load data on database """

        if data_filter is None:
            data_filter = []
        csv = open(file_path, 'r')  # path to csv file
        csv.next()
        factory = TestLoaderFactory()
        loader = factory.getModelLoader(model)(csv, log, settings.GTFS_VERSION)
        loader.load(data_filter)
        csv.close()
        log.close()

    def insertServicesOnDatabase(self, route_list):
        """ load services """

        log = open(self.LOG_FILE_NAME, 'w')
        file_path = os.path.join(self.GTFS_PATH, 'services.csv')
        model = 'service'

        self.__load_data(model, file_path, log, route_list)

    def insertBusstopsOnDatabase(self, stop_list):
        """ load bus stops """

        log = open(self.LOG_FILE_NAME, 'w')
        file_path = os.path.join(self.GTFS_PATH, 'busstop.csv')
        model = 'busstop'

        self.__load_data(model, file_path, log, stop_list)

    def insertServicesByBusstopsOnDatabase(self, stop_list):
        """ load services by bus stops """

        log = open(self.LOG_FILE_NAME, 'w')
        file_path = os.path.join(self.GTFS_PATH, 'servicesbybusstop.csv')
        model = 'servicesbybusstop'

        self.__load_data(model, file_path, log, stop_list)

    def insertServiceStopDistanceOnDatabase(self, stop_list):
        """ load service stop distance data by service with direction """

        log = open(self.LOG_FILE_NAME, 'w')
        file_path = os.path.join(self.GTFS_PATH, 'servicestopdistance.csv')
        model = 'servicestopdistance'

        self.__load_data(model, file_path, log, stop_list)

    def insertServiceLocationOnDatabase(self, routes_with_direction):
        """ load service location data by service with direction """

        log = open(self.LOG_FILE_NAME, 'w')
        file_path = os.path.join(self.GTFS_PATH, 'servicelocation.csv')
        model = 'servicelocation'

        self.__load_data(model, file_path, log, routes_with_direction)

    def askForMachineId(self, license_plate):
        """ simulate a request to get machine id based on its licence plate """
        url = '/android/getUUID/'
        c = Client()
        url = url + '/'.join([license_plate])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)
        machine_id = json_response['uuid']

        return machine_id

    def createBusAndAssignmentOnDatabase(self, phone_id, route, license_plate):
        """ create a bus object and assignment object """
        self.getInBusWithLicencePlate(phone_id, route, license_plate)

    def getInBusWithLicencePlate(
            self, phone_id, route, license_plate, time=timezone.now()):
        """ create a user on bus in database """
        machine_id = self.askForMachineId(license_plate)
        url = '/android/requestToken/v2/'
        request = self.factory.get(url)
        request.user = AnonymousUser()

        view = RequestTokenV2()
        response = view.get(request, phone_id, route, machine_id, None, None, None, None, time)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)
        token = json_response['token']

        return token

    def getInBusWithMachineId(self, phone_id, route, machine_id):
        """ create a user on bus in database """
        url = '/android/requestToken/v2/'
        c = Client()
        url = url + '/'.join([phone_id, route, machine_id])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)
        token = json_response['token']

        return token

    def getInBusWithLicencePlateByPost(
            self, phone_id, route, license_plate, bus_longitude=None, bus_latitude=None,
            user_id=None, session_token=None):
        """ create a user on bus in database """
        machine_id = self.askForMachineId(license_plate)
        url = '/android/requestToken/v2'
        c = Client()

        data = {'phoneId': phone_id,
                'route': route,
                'machineId': machine_id
                }
        if user_id is not None:
            data['userId'] = user_id
            data['sessionToken'] = session_token
        if bus_longitude is not None:
            data["longitude"] = bus_longitude
        if bus_latitude is not None:
            data["latitude"] = bus_latitude

        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)
        token = json_response['token']

        return token

    def getInBusWithMachineIdByPost(self, phone_id, route, machine_id, bus_longitude=None, bus_latitude=None,
                                    user_id=None, session_token=None):
        """ create a user on bus in database """
        url = '/android/requestToken/v2'
        c = Client()

        data = {'phoneId': phone_id, 'route': route, 'machineId': machine_id}
        if user_id is not None:
            data['userId'] = user_id,
            data['sessionToken'] = session_token
        if bus_longitude is not None:
            data["longitude"] = bus_longitude
        if bus_latitude is not None:
            data["latitude"] = bus_latitude

        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)
        token = json_response['token']

        return token

    def endRoute(self, token):
        """ revoke token used to identify a trip """
        url = '/android/endRoute/'
        c = Client()
        url = url + token
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def endRouteByPost(self, token, purgeCause):
        """ revoke token used to identify a trip """
        url = '/android/endRoute'
        c = Client()
        url = url
        data = {
            'token': token,
            'purgeCause': purgeCause
        }
        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def sendFakeTrajectoryOfToken(self, travel_token, poses=None, user_id=None, session_token=None):
        """ send fake positions for user travel """
        now = timezone.now()
        times = [now,
                 now - timezone.timedelta(minutes=5),
                 now - timezone.timedelta(minutes=10),
                 now - timezone.timedelta(minutes=15),
                 now - timezone.timedelta(minutes=20),
                 now - timezone.timedelta(minutes=25),
                 now - timezone.timedelta(minutes=30),
                 now - timezone.timedelta(minutes=35),
                 now - timezone.timedelta(minutes=40)]
        fTimes = []
        for time in times:
            fTimes.append(time.strftime("%Y-%m-%dT%X"))

        if poses is None:
            poses = {"poses": [
                {"latitud": -33.458771, "longitud": -70.676266,
                 "timeStamp": fTimes[0], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.458699, "longitud": -70.675708,
                 "timeStamp": fTimes[1], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.458646, "longitud": -70.674678,
                 "timeStamp": fTimes[2], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.458646, "longitud": -70.673799,
                 "timeStamp": fTimes[3], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.458413, "longitud": -70.671631,
                 "timeStamp": fTimes[4], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.457983, "longitud": -70.669035,
                 "timeStamp": fTimes[5], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.457518, "longitud": -70.666718,
                 "timeStamp": fTimes[6], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.457196, "longitud": -70.664636,
                 "timeStamp": fTimes[7], "inVehicleOrNot": "vehicle"},
                {"latitud": -33.457070, "longitud": -70.660559,
                 "timeStamp": fTimes[8], "inVehicleOrNot": "vehicle"}]}

        c = Client()
        url = '/android/sendTrajectory'
        data = {'pToken': travel_token,
                'pTrajectory': json.dumps(poses, cls=TranSappJSONEncoder)
                }
        if user_id is not None:
            data["userId"] = user_id
            data["sessionToken"] = session_token
        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def sendFakeTrajectoryOfTokenV2(self, travelToken, poses=None, user_id=None, session_token=None):
        """ send fake positions for user travel """
        times = []
        for _ in range(9):
            times.append(random.randint(-40, -1))

        if poses is None:
            poses = {"poses": [
                {"latitude": -33.458771, "longitude": -70.676266,
                 "timeDelay": times[0], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.458699, "longitude": -70.675708,
                 "timeDelay": times[1], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.458646, "longitude": -70.674678,
                 "timeDelay": times[2], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.458646, "longitude": -70.673799,
                 "timeDelay": times[3], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.458413, "longitude": -70.671631,
                 "timeDelay": times[4], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.457983, "longitude": -70.669035,
                 "timeDelay": times[5], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.457518, "longitude": -70.666718,
                 "timeDelay": times[6], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.457196, "longitude": -70.664636,
                 "timeDelay": times[7], "inVehicleOrNot": "vehicle"},
                {"latitude": -33.457070, "longitude": -70.660559,
                 "timeDelay": times[8], "inVehicleOrNot": "vehicle"}]}

        c = Client()
        url = '/android/sendTrajectory/v2'
        data = {'token': travelToken,
                'trajectory': json.dumps(poses, cls=TranSappJSONEncoder)
                }
        if user_id is not None:
            data["userId"] = user_id
            data["sessionToken"] = session_token
        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def setDirection(self, travelKey, direction):
        """ set direction of trip """
        url = '/android/setDirection'
        c = Client()
        url = url
        response = c.post(url, {'pToken': travelKey, 'pDirection': direction})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def evaluateTrip(self, travelToken, evaluation, user_id=None, session_token=None):
        """ send trip evaluation """

        url = '/android/evaluateTrip'
        request = self.factory.post(url)
        request.user = AnonymousUser()

        c = Client()
        data = {
            'token': travelToken,
            'evaluation': evaluation
        }
        if user_id is not None:
            data["userId"] = user_id
            data["sessionToken"] = session_token
        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    """
       BUS EVENT METHODS V1
    """

    def reportEvent(self, phone_id, route, licencePlate, event_code):
        """ report an event with the old version  """
        url = '/android/reportEventBus/'
        c = Client()
        url = url + '/'.join([phone_id, route, licencePlate, event_code, EventRegistration.CONFIRM])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def confirmOrDeclineEvent(self, phone_id, route, licencePlate, event_code, confirm_or_decline):
        """ report an event with the old version  """
        url = '/android/reportEventBus/'
        c = Client()
        url = url + '/'.join([phone_id, route, licencePlate, event_code, confirm_or_decline])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def requestEventsForBus(self, route, licencePlate):
        """ ask for events related to machine id """
        url = '/android/requestEventsForBus/'
        c = Client()
        url = url + '/'.join([licencePlate, route])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    """
       BUS EVENT METHODS V2
    """

    def reportEventV2(self, phone_id, machine_id, route, event_code):
        """ report an event with the new version  """
        url = '/android/reportEventBus/v2/'
        c = Client()
        url = url + '/'.join([phone_id, machine_id, route,
                              event_code, EventRegistration.CONFIRM])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def confirmOrDeclineEventV2(
            self, phone_id, machine_id, route, event_code, confirm_or_decline):
        """ confirm or decline an event with the new version  """
        url = '/android/reportEventBus/v2/'
        c = Client()
        url = url + '/'.join([phone_id, machine_id, route, event_code, confirm_or_decline])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def requestEventsForBusV2(self, machine_id):
        """ ask for events related to machine id """
        url = '/android/requestEventsForBus/v2/'
        c = Client()
        url = url + '/'.join([machine_id])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    """
        STOP METHODS
    """

    def reportStopEvent(self, phone_id, stop_code, event_code, aditionalInfo=None):
        """ report an event for stop """
        url = '/android/reportEventBusStop/'
        c = Client()
        if aditionalInfo is None:
            params = [phone_id, stop_code, event_code, EventRegistration.CONFIRM]
        else:
            params = [phone_id, stop_code, aditionalInfo, event_code, EventRegistration.CONFIRM]
        url = url + '/'.join(params)
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def confirmOrDeclineStopEvent(
            self, phone_id, stop_code, event_code, confirm_or_decline):
        """ confirm or decline an event for stop """
        url = '/android/reportEventBusStop/'
        c = Client()
        url = url + '/'.join([phone_id, stop_code, event_code, confirm_or_decline])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def requestEventsForBusStop(self, code):
        """ ask for events related to bus stop """
        url = '/android/requestEventsForBusStop/'
        c = Client()
        url = url + code
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    """
        BUS EVENT METHODS BY POST
    """

    def reportEventV2ByPost(self, phone_id, machine_id, route, event_code, user_id=None, session_token=None):
        """ report an event with the new version  """
        url = '/android/reportEventBus/v2'
        c = Client()
        data = {'phoneId': phone_id,
                'machineId': machine_id,
                'service': route,
                'eventId': event_code,
                'vote': EventRegistration.CONFIRM
                }
        if user_id is not None:
            data["userId"] = user_id
            data["sessionToken"] = session_token
        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def confirmOrDeclineEventV2ByPost(
            self, phone_id, machine_id, route, event_code, confirm_or_decline, user_id, session_token):
        """ confirm or decline an event with the new version  """
        url = '/android/reportEventBus/v2'
        c = Client()
        data = {'phoneId': phone_id,
                'machineId': machine_id,
                'service': route,
                'eventId': event_code,
                'vote': confirm_or_decline,
                'userId': user_id,
                'sessionToken': session_token}
        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def reportStopEventByPost(self, phone_id, stop_code, event_code, user_id, session_token):
        """ report an event for stop """
        url = '/android/reportEventBusStop'
        c = Client()
        data = {'phoneId': phone_id,
                'stopCode': stop_code,
                'eventId': event_code,
                'vote': EventRegistration.CONFIRM,
                'userId': user_id,
                'sessionToken': session_token}

        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def confirmOrDeclineStopEventByPost(
            self, phone_id, stop_code, event_code, confirm_or_decline, user_id, session_token):
        """ confirm or decline an event for stop """
        url = '/android/reportEventBusStop'
        c = Client()
        data = {'phoneId': phone_id,
                'stopCode': stop_code,
                'eventId': event_code,
                'vote': confirm_or_decline,
                'userId': user_id,
                'sessionToken': session_token}

        response = c.post(url, data)

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response

    def createTranSappUsers(self, user_quantity):
        """ create @quantity users and put the user asked in @userPosition """
        users = []

        level, created = Level.objects.get_or_create(position=1,
                                                     defaults={'name': 'level 1', 'minScore': 0, 'maxScore': 1000})

        for index in range(user_quantity):
            name = "name{}".format(index)
            nickname = "nickname{}".format(index)
            user_id = "userId{}".format(index)
            session_token = uuid.uuid4()
            phone_id = uuid.uuid4()
            user = TranSappUser.objects.create(userId=user_id,
                                               sessionToken=session_token, name=name, nickname=nickname,
                                               phoneId=phone_id, accountType=TranSappUser.FACEBOOK,
                                               level=level, globalScore=(100 * (index + 1)),
                                               globalPosition=(user_quantity - 1))
            users.append(user)

        return users

    def report(self, text, image, format_image, phone_id, report_info):
        url = '/android/registerReport'
        data = {
            "text": text,
            "img": image,
            "ext": format_image,
            "userId": phone_id,
            "reportInfo": report_info
        }
        response = Client().post(url, data)

        self.test.assertEqual(response.status_code, 200)

        return json.loads(response.content)

    def reportV2(self, text, image, format_image, phone_id, report_info, user_id=None, session_token=None):
        url = '/android/registerReport/v2'
        data = {
            "text": text,
            "img": image,
            "ext": format_image,
            "phoneId": phone_id,
            "reportInfo": report_info
        }
        if user_id is not None:
            data["userId"] = user_id
            data["sessionToken"] = session_token
        response = Client().post(url, data)

        self.test.assertEqual(response.status_code, 200)

        return json.loads(response.content)

    def requestNearbyBuses(self, phone_id, stop_code):
        """ ask for nearbybuses """
        url = '/android/nearbyBuses/'
        c = Client()
        url = url + "/".join([phone_id, stop_code])
        response = c.get(url, {})

        self.test.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content)

        return json_response
