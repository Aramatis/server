import os, sys
from Loaders.LoaderFactory import LoaderFactory
from Loaders.ModelLoaders import LoadEvents
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from AndroidRequests.models import *
from AndroidRequests.allviews.EventsByBus import EventsByBus

query = EventsByBus()

bus = Bus.objects.get(registrationPlate="BJFF58", service="507")
print "the bus", bus


response =  query.getEventForBus(bus)

for cont in response:
 print cont
 print "----"
