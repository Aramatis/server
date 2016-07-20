from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

# import my stuff
from MapLocationOfUsers.views import MapHandler, GetMapPositions, GetMapTrajectory
from AndroidRequests.models import DevicePositionInTime, PoseInTrajectoryOfToken
#views
from AndroidRequests.allviews.RequestToken import RequestToken
from AndroidRequests.allviews.EndRoute import EndRoute
from AndroidRequests.allviews.SendPoses import SendPoses
from AndroidRequests.allviews.RegisterEventBus import RegisterEventBus
from AndroidRequests.allviews.RegisterEventBusStop import RegisterEventBusStop

import json

class GetMapPositionsTest(TestCase):
    def setUp(self):
        self.userId = "067e6162-3b6f-4ae2-a171-2470b63dff00"

        DevicePositionInTime.objects.create(userId = self.userId, longitud = 3.4, latitud = 5.2, timeStamp = timezone.now())
        DevicePositionInTime.objects.create(userId = self.userId, longitud = 3.4, latitud = 5.2, timeStamp = timezone.now())
        # this should not be answered
        DevicePositionInTime.objects.create(userId = self.userId, longitud = 3.3, latitud = 4.2, timeStamp = timezone.now()\
        	-timezone.timedelta(minutes=11))
        self.factory = RequestFactory()

    def test_getPositions(self):
    	'''This test the response of the current poses'''

        request = self.factory.get('/map/activeuserpose')
        request.user = AnonymousUser()

        responseView = GetMapPositions()
        response = responseView.get(request)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        for postitionRes in data:
        	self.assertEqual(postitionRes['longitud'],3.4)
        	self.assertEqual(postitionRes['latitud'],5.2)

    def test_showMap(self):
    	'''this test is for testing the response of the map view'''

        request = self.factory.get('/map/show')
        request.user = AnonymousUser()

        responseView = MapHandler()
        response = responseView.get(request)

        self.assertEqual(response.status_code, 200)

    def test_getGetMapTrajectory(self):
        '''this test the trajectory that the server gives to the map. '''

        timeStampNow = str(timezone.localtime(timezone.now()))
        timeStampNow = timeStampNow[0:19]
        testPoses = {"poses":[
        {"latitud":-33.458771,"longitud" : -70.676266, "timeStamp":str(timeStampNow)    ,"inVehicleOrNot":"vehicle"},\
        {"latitud":-33.458699,"longitud" : -70.675708, "timeStamp":"2015-10-01T18:10:10","inVehicleOrNot":"vehicle"},\
        {"latitud":-33.458646,"longitud" : -70.674678, "timeStamp":"2015-10-01T18:10:15","inVehicleOrNot":"vehicle"},\
        {"latitud":-33.458646,"longitud" : -70.673799, "timeStamp":"2015-10-01T18:10:20","inVehicleOrNot":"vehicle"},\
        {"latitud":-33.458413,"longitud" : -70.671631, "timeStamp":"2015-10-01T18:10:24","inVehicleOrNot":"vehicle"},\
        {"latitud":-33.457983,"longitud" : -70.669035, "timeStamp":"2015-10-01T18:10:30","inVehicleOrNot":"vehicle"},\
        {"latitud":-33.457518,"longitud" : -70.666718, "timeStamp":"2015-10-01T18:10:35","inVehicleOrNot":"vehicle"},\
        {"latitud":-33.457196,"longitud" : -70.664636, "timeStamp":"2015-10-01T18:10:40","inVehicleOrNot":"vehicle"},\
        {"latitud":-33.457070,"longitud" : -70.660559, "timeStamp":str(timeStampNow)    ,"inVehicleOrNot":"vehicle"}]}

        testTokens = []

        request = self.factory.get('/android/requestToken')
        request.user = AnonymousUser()

        for cont in range(6):
            reponseView = RequestToken()
            response = reponseView.get(request, self.userId, '503', 'ZZZZ00')

            jsonContent = json.loads(response.content)
            testToken = jsonContent['token']
            testTokens.append(testToken)

        # save last token
        timeOutToken = testTokens[-1]

        for cont in range(6):
            request = self.factory.get('/android/sendTrajectoy')
            request.user = AnonymousUser()

            reponseView = SendPoses()
            request.POST = {}
            request.POST['pToken'] = testTokens[cont]
            request.POST['pTrajectory'] = json.dumps(testPoses)
            request.method = 'POST'
            response = reponseView.get(request)

            request = self.factory.get('/android/endRoute/')
            request.user = AnonymousUser()
            reponseView = EndRoute()
            response = reponseView.get(request,testTokens[cont])

        nonTrajectory = PoseInTrajectoryOfToken.objects.filter(token=timeOutToken)
        for data in nonTrajectory:
            data.timeStamp = data.timeStamp - timezone.timedelta(minutes=11)
            data.save()

        request = self.factory.get('/map/activetrajectory')
        request.user = AnonymousUser()

        reponseView = GetMapTrajectory()
        response = reponseView.get(request)

        responseMessage = json.loads(response.content)

        # all tokens given by GetMapTrajectory are different of timeOutToken
        for aMsg in responseMessage:
            self.assertEqual(aMsg['token'] != timeOutToken , True)

        self.assertEqual(len(responseMessage), len(testTokens)-1)

