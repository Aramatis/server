from django.http import JsonResponse
from django.views.generic import View
from django.utils import timezone

#python utilities
import requests
from random import uniform

# my stuff
# import DB's models
from AndroidRequests.models import Event

class RequestEventsToNotified(View):
    """This class sends the event that can be notified in a given time.
    For example if I'm in a bus stop, I can report some events regarding what I see,
    so I report things from the bus stop and what I can see of the bus. If i'm on a bus
    I can report detailed problems about the bus."""

    def get(self, request, pWhich):

        events = []

        if pWhich == 'stopstop':
            events = Event.objects.filter(eventType='busStop')
        elif pWhich == 'stopbus':
            events = Event.objects.filter(eventType='bus', origin='o')
        elif pWhich == 'busbus':
            events = Event.objects.filter(eventType='bus', origin='i')

        response = []

        for data in events:
            response.append(data.getDictionary())

        return JsonResponse(response, safe=False)



