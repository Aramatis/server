from django.http import JsonResponse
from django.views.generic import View

from AndroidRequests.models import Event
from AndroidRequests.encoder import TranSappJSONEncoder


class RequestEventsToNotified(View):
    """This class sends the event that can be notified in a given time.
    For example if I'm in a bus stop, I can report some events regarding what I see,
    so I report things from the bus stop and what I can see of the bus. If i'm on a bus
    I can report detailed problems about the bus."""

    def get(self, request, which):

        events = []

        if which == 'stopstop':
            events = Event.objects.filter(eventType=Event.STOP_TYPE)
        elif which == 'stopbus':
            events = Event.objects.filter(eventType=Event.BUS_TYPE, origin='o')
        elif which == 'busbus':
            events = Event.objects.filter(eventType=Event.BUS_TYPE, origin='i')

        response = []

        for data in events:
            response.append(data.getDictionary())

        return JsonResponse(response, safe=False, encoder=TranSappJSONEncoder)
