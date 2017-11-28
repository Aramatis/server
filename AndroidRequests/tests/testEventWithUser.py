from django.test import TransactionTestCase

from AndroidRequests.models import StadisticDataFromRegistrationBus, StadisticDataFromRegistrationBusStop, Level, \
    ScoreEvent, TranSappUser, EventRegistration
from AndroidRequests.tests.testHelper import TestHelper


class EventWithUserTestCase(TransactionTestCase):
    """ test for DevicePositionInTime model """
    fixtures = ["events"]

    def setUp(self):
        """ this method will automatically call for every single test """
        # create events
        self.test = TestHelper(self)
        self.eventBusCode = 'evn00201'

        # create levels 
        level = Level.objects.create(name='level 1', minScore=0, maxScore=1000, position=1)

        # create score event for eventCode
        self.score = 100
        ScoreEvent.objects.create(code=self.eventBusCode, score=self.score)

        self.phone_id = '1df6e1b6a1b840d689b364119db3fb7c'
        license_plate = 'AA1111'
        self.service = '507'
        self.machineId = self.test.askForMachineId(license_plate)
        self.token = self.test.getInBusWithMachineId(self.phone_id, self.service, self.machineId)

        # create TranSappUser
        self.userId = '123456789'
        self.sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=self.userId, name='Te st', email='a@b.com',
                                    phoneId=self.phone_id, accountType=TranSappUser.FACEBOOK,
                                    level=level, sessionToken=self.sessionToken, globalPosition=1)

    def test_userAssignedToBusEvent(self):
        """This method check that user was assigned to bus event """

        self.test.reportEventV2ByPost(self.phone_id, self.machineId,
                                      self.service, self.eventBusCode, self.userId, self.sessionToken)

        event_obj = StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all()[0]
        self.assertEqual(event_obj.tranSappUser.userId, self.userId)

        # we will vote -1
        self.test.confirmOrDeclineEventV2ByPost(self.phone_id, self.machineId,
                                                self.service, self.eventBusCode, EventRegistration.DECLINE, self.userId,
                                                self.sessionToken)

        event_obj = \
            StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(event_obj.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineEventV2ByPost(self.phone_id, self.machineId,
                                                self.service, self.eventBusCode, EventRegistration.CONFIRM, self.userId,
                                                self.sessionToken)

        event_obj = \
            StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(event_obj.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineEventV2ByPost(self.phone_id, self.machineId,
                                                self.service, self.eventBusCode, EventRegistration.CONFIRM, None, None)

        event_obj = \
            StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(event_obj.tranSappUser, None)

    def test_userAssignedToStopEvent(self):
        """This method check that user was assigned to stop event """

        stop_code = 'PA459'
        self.test.insertBusstopsOnDatabase([stop_code])
        event_stop_code = 'evn00010'
        ScoreEvent.objects.create(code=event_stop_code, score=100)

        self.test.reportStopEventByPost(self.phone_id, stop_code,
                                        event_stop_code, self.userId, self.sessionToken)

        event_obj = StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all()[0]
        self.assertEqual(event_obj.tranSappUser.userId, self.userId)

        # we will vote -1
        self.test.confirmOrDeclineStopEventByPost(self.phone_id, stop_code,
                                                  event_stop_code, EventRegistration.DECLINE, self.userId,
                                                  self.sessionToken)

        event_obj = \
            StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(event_obj.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineStopEventByPost(self.phone_id, stop_code,
                                                  event_stop_code, EventRegistration.CONFIRM, self.userId,
                                                  self.sessionToken)

        event_obj = \
            StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(event_obj.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineStopEventByPost(self.phone_id, stop_code,
                                                  event_stop_code, EventRegistration.CONFIRM, None, None)

        event_obj = \
            StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(event_obj.tranSappUser, None)
