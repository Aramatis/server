from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

# import my stuff
from MapLocationOfUsers.views import MapHandler, GetMapPositions
from AndroidRequests.models import DevicePositionInTime

import json

class GetMapPositionsTest(TestCase):
    def setUp(self):
        DevicePositionInTime.objects.create(longitud = 3.4, latitud = 5.2, timeStamp = timezone.now())
        DevicePositionInTime.objects.create(longitud = 3.4, latitud = 5.2, timeStamp = timezone.now())
        # this should not be answered
        DevicePositionInTime.objects.create(longitud = 3.3, latitud = 4.2, timeStamp = timezone.now()\
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