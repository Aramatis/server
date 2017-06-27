import json

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

# views
from AndroidRequests.allviews.RequestEventsToNotified import RequestEventsToNotified
# my stuff
from AndroidRequests.models import Event


class RequestEventsToNotifiedTestCase(TestCase):
    """ test for events-to-notified view """

    def setUp(self):

        self.factory = RequestFactory()

        self.request = self.factory.post('/android/requestEventsToNotified/')
        self.request.user = AnonymousUser()
        self.reponseView = RequestEventsToNotified()

        # one event for bus stop, bus from bus stop and bus from bus
        self.eventBusStop = Event.objects.create(id='ebs', name='event for bus stop',
                                                 description='event for bus stop from bus stop', eventType='busStop', origin='o')
        self.eventBusFromBusStop = Event.objects.create(id='bfbs', name='event for bus',
                                                        description='event for bus from bus stop', eventType='bus', origin='o')
        self.eventBusFromBus = Event.objects.create(id='bfb', name='event for bus',
                                                    description='event for bus from bus', eventType='bus', origin='i')

    def test_request_events_for_bus_stop(self):
        which = 'stopstop'
        response = self.reponseView.get(self.request, which)
        jsonResponse = json.loads(response.content)

        element = jsonResponse[0]
        self.assertEqual(len(jsonResponse), 1)
        self.assertEqual(element['name'], self.eventBusStop.name)
        self.assertEqual(element['description'], self.eventBusStop.description)
        self.assertEqual(element['eventcode'], self.eventBusStop.id)

    def test_request_events_for_bus_from_bus_stop(self):
        which = 'stopbus'
        response = self.reponseView.get(self.request, which)
        jsonResponse = json.loads(response.content)

        element = jsonResponse[0]
        self.assertEqual(len(jsonResponse), 1)
        self.assertEqual(element['name'], self.eventBusFromBusStop.name)
        self.assertEqual(
            element['description'],
            self.eventBusFromBusStop.description)
        self.assertEqual(element['eventcode'], self.eventBusFromBusStop.id)

    def test_request_events_for_bus_from_bus(self):
        which = 'busbus'
        response = self.reponseView.get(self.request, which)
        jsonResponse = json.loads(response.content)

        element = jsonResponse[0]
        self.assertEqual(len(jsonResponse), 1)
        self.assertEqual(element['name'], self.eventBusFromBus.name)
        self.assertEqual(
            element['description'],
            self.eventBusFromBus.description)
        self.assertEqual(element['eventcode'], self.eventBusFromBus.id)
