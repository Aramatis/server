from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

# my stuff
from AndroidRequests.models import DevicePositionInTime
# Create your tests here.

class DevicePositionInTimeTest(TestCase):
    def setUp(self):
        self.time = timezone.now()
        DevicePositionInTime.objects.create(longitud = 3.5, latitud = 5.2, timeStamp = self.time)
        DevicePositionInTime.objects.create(longitud = 3.4, latitud = 5.2, timeStamp = self.time)
        # this should not be answered
        DevicePositionInTime.objects.create(longitud = 3.3, latitud = 4.2, timeStamp = self.time\
        	-timezone.timedelta(minutes=11))
        self.factory = RequestFactory()


    def test_consistencyModelDevicePositionInTime(self):
        '''This methos test the database for the model DevicePositionInTime'''

        longituds = [3.5, 3.4, 3.3]
        latituds = [5.2, 5.2, 4.2]
        timeStamps = [self.time,self.time,self.time-timezone.timedelta(minutes=11)]

        for cont in range(3):
        	devicePosition = DevicePositionInTime.objects.get(longitud = longituds[cont])
        	self.assertEqual(devicePosition.latitud, latituds[cont])
        	self.assertEqual(devicePosition.timeStamp, timeStamps[cont])

