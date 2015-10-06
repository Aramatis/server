from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import json

# my stuff
from AndroidRequests.models import DevicePositionInTime, ActiveToken
from AndroidRequests.views import EndRoute, RequestToken, SendPoses
# Create your tests here.

class DevicePositionInTimeTest(TestCase):
    def setUp(self):
        # for testing requests inside the project
        self.factory = RequestFactory()

        # iniital config for DevicePositionInTime
        self.time = timezone.now()
        DevicePositionInTime.objects.create(longitud = 3.5, latitud = 5.2, timeStamp = self.time)
        DevicePositionInTime.objects.create(longitud = 3.4, latitud = 5.2, timeStamp = self.time)
        # this should not be answered
        DevicePositionInTime.objects.create(longitud = 3.3, latitud = 4.2, timeStamp = self.time\
        	-timezone.timedelta(minutes=11))        

        # initial config for ActiveToken



    def test_consistencyModelDevicePositionInTime(self):
        '''This method test the database for the DevicePositionInTime model'''

        longituds = [3.5, 3.4, 3.3]
        latituds = [5.2, 5.2, 4.2]
        timeStamps = [self.time,self.time,self.time-timezone.timedelta(minutes=11)]

        for cont in range(3):
        	devicePosition = DevicePositionInTime.objects.get(longitud = longituds[cont])
        	self.assertEqual(devicePosition.latitud, latituds[cont])
        	self.assertEqual(devicePosition.timeStamp, timeStamps[cont])

    def test_consistencyModelActiveToken(self):
        '''This method test the database for the ActiveToken model'''
        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        reponseView = RequestToken()
        response = reponseView.get(request)

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        testToken = testToken['token']

        self.assertEqual(ActiveToken.objects.filter(token=testToken).exists(), True)

        request = self.factory.get('/android/endRoute/' + testToken)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,testToken)

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'], 'Trip ended.')

    def test_consistencyModelPoseInTrajectoryOfToken(self):
        '''this method test the PoseInTrajectoryOfToken'''

        testPoses = {"poses":[{"latitud":-33.458771,"longitud" : -70.676266, "timeStamp":"2015-10-01T18:10:00"},\
        {"latitud":-33.458699,"longitud" : -70.675708, "timeStamp":"2015-10-01T18:10:10"},{"latitud":-33.458646,\
        "longitud" : -70.674678, "timeStamp":"2015-10-01T18:10:15"},{"latitud":-33.458646,"longitud" : -70.673799, \
        "timeStamp":"2015-10-01T18:10:20"},{"latitud":-33.458413,"longitud" : -70.671631, \
        "timeStamp":"2015-10-01T18:10:24"},{"latitud":-33.457983,"longitud" : -70.669035, \
        "timeStamp":"2015-10-01T18:10:30"},{"latitud":-33.457518,"longitud" : -70.666718, \
        "timeStamp":"2015-10-01T18:10:35"},{"latitud":-33.457196,"longitud" : -70.664636, \
        "timeStamp":"2015-10-01T18:10:40"},{"latitud":-33.457070,"longitud" : -70.660559, \
        "timeStamp":"2015-10-01T18:10:50"}]}

        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        reponseView = RequestToken()
        response = reponseView.get(request)

        self.assertEqual(response.status_code, 200)

        testToken = json.loads(response.content)
        testToken = testToken['token']

        request = self.factory.get('/android/sendTrajectoy')
        request.user = AnonymousUser()

        reponseView = SendPoses()#pToken, pTrajectory
        response = reponseView.get(request,testToken,json.dumps(testPoses))

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'],'Poses were register.')

        # remove the token
        request = self.factory.get('/android/endRoute/' + testToken)
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,testToken)

        request = self.factory.get('/android/sendTrajectoy')
        request.user = AnonymousUser()

        reponseView = SendPoses()#pToken, pTrajectory
        response = reponseView.get(request,testToken,json.dumps(testPoses))

        contentResponse = json.loads(response.content)
        self.assertEqual(contentResponse['response'],'Token doesn\'t exist.')

    def test_EndRoute(self):
        '''this method test the EndRoute request when it fails.'''
        request = self.factory.get('/android/endRoute/')
        request.user = AnonymousUser()

        reponseView = EndRoute()
        response = reponseView.get(request,'01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567')
        
        contentResponse = json.loads(response.content)
        contentResponse = contentResponse['response']

        self.assertEqual(contentResponse,'Token doesn\'t exist.')






