from django.core.management.base import BaseCommand
#from django.db.models.loading import get_model
#from django.apps.apps import get_model
from django.core import serializers
from AndroidRequests.models import EventForBusStop, EventForBus
from django.utils import timezone
from datetime import timedelta
import csv
import json



class Command(BaseCommand):

    def handle(self, *args, **options):
        query_buss = EventForBus.objects.filter(timeStamp__gt = (timezone.now() - timedelta(hours=5)))
        query_buss_stop = EventForBusStop.objects.filter(timeStamp__gt = (timezone.now() - timedelta(hours=5)))
        



def dump(qs, outfile_path):

    model = qs.model
    writer = csv.writer(open(outfile_path, 'w'))
    headers = []
    for field in model._meta.fields:
    	headers.append(field.name)
    writer.writerow(headers)

    for obj in qs:
    	row = []
    	for field in headers:
    		val = getattr(obj, field)
    		if callable(val):
    			val = val()
    		if type(val) == unicode:
    			val = val.encode("utf-8")
    		row.append(val)
    	writer.writerow(row)