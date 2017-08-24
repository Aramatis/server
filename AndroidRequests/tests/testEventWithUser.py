from django.test import TransactionTestCase

from AndroidRequests.models import StadisticDataFromRegistrationBus, StadisticDataFromRegistrationBusStop, Level, \
    ScoreEvent, TranSappUser, EventRegistration
from AndroidRequests.tests.testHelper import TestHelper


class EventWithUserTestCase(TransactionTestCase):
    """ test for DevicePositionInTime model """

    def setUp(self):
        """ this method will automatically call for every single test """
        # create events
        self.test = TestHelper(self)
        self.test.insertEventsOnDatabase()
        self.eventBusCode = 'evn00201'

        # create levels 
        level = Level.objects.create(name='level 1', minScore=0, maxScore=1000, position=1)

        # create score event for eventCode
        self.score = 100
        ScoreEvent.objects.create(code=self.eventBusCode, score=self.score)

        self.phoneId = '1df6e1b6a1b840d689b364119db3fb7c'
        licencePlate = 'AA1111'
        self.service = '507'
        self.machineId = self.test.askForMachineId(licencePlate)
        self.token = self.test.getInBusWithMachineId(self.phoneId, self.service, self.machineId)

        # create TranSappUser
        self.userId = '123456789'
        self.sessionToken = '4951e324-9ab4-4f1f-845c-04259785b58b'
        TranSappUser.objects.create(userId=self.userId, name='Te st', email='a@b.com',
                                    phoneId=self.phoneId, accountType=TranSappUser.FACEBOOK,
                                    level=level, sessionToken=self.sessionToken)

    def test_userAssignedToBusEvent(self):
        '''This method check that user was assigned to bus event '''

        self.test.reportEventV2ByPost(self.phoneId, self.machineId,
                                      self.service, self.eventBusCode, self.userId, self.sessionToken)

        eventRecord = StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all()[0]
        self.assertEqual(eventRecord.tranSappUser.userId, self.userId)

        # we will vote -1
        self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                self.service, self.eventBusCode, EventRegistration.DECLINE, self.userId,
                                                self.sessionToken)

        eventRecord = \
            StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(eventRecord.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                self.service, self.eventBusCode, EventRegistration.CONFIRM, self.userId,
                                                self.sessionToken)

        eventRecord = \
            StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(eventRecord.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineEventV2ByPost(self.phoneId, self.machineId,
                                                self.service, self.eventBusCode, EventRegistration.CONFIRM, None, None)

        eventRecord = \
            StadisticDataFromRegistrationBus.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(eventRecord.tranSappUser, None)

    def test_userAssignedToStopEvent(self):
        '''This method check that user was assigned to stop event '''

        stopCode = 'PA459'
        self.test.insertBusstopsOnDatabase([stopCode])
        eventStopCode = 'evn00010'
        ScoreEvent.objects.create(code=eventStopCode, score=100)

        self.test.reportStopEventByPost(self.phoneId, stopCode,
                                        eventStopCode, self.userId, self.sessionToken)

        eventRecord = StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all()[0]
        self.assertEqual(eventRecord.tranSappUser.userId, self.userId)

        # we will vote -1
        self.test.confirmOrDeclineStopEventByPost(self.phoneId, stopCode,
                                                  eventStopCode, EventRegistration.DECLINE, self.userId,
                                                  self.sessionToken)

        eventRecord = \
            StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(eventRecord.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineStopEventByPost(self.phoneId, stopCode,
                                                  eventStopCode, EventRegistration.CONFIRM, self.userId,
                                                  self.sessionToken)

        eventRecord = \
            StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(eventRecord.tranSappUser.userId, self.userId)

        # we will vote +1
        self.test.confirmOrDeclineStopEventByPost(self.phoneId, stopCode,
                                                  eventStopCode, EventRegistration.CONFIRM, None, None)

        eventRecord = \
            StadisticDataFromRegistrationBusStop.objects.select_related('tranSappUser').all().order_by('-timeStamp')[0]
        self.assertEqual(eventRecord.tranSappUser, None)
