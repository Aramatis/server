from django.core.management.base import BaseCommand
from django.core import serializers


class Command(BaseCommand):

    def handle(self, *args, **options):
        list_json = [
            'dump_Report.json',
            'dump_EventForBusStop.json',
            'dump_StadisticDataFromRegistrationBusStop.json',
            'dump_EventForBusv2.json',
            'dump_StadisticDataFromRegistrationBus.json',
            'dump_Busassignment.json',
            'dump_Busv2.json'
        ]
        self.from_JSON(self.reports_cb, list_json)


    def from_JSON(self, callback, filenames):
        for filename in filenames:
            print("loading data from: " + filename)
            cnt = 0
            with open(filename, 'r') as file:
                for deserialized_object in serializers.deserialize("json", file, ignorenonexistent=True):
                    callback(deserialized_object)
                    cnt += 1
            print(" . . . loaded " + str(cnt) + " rows.")


    def reports_cb(self, deserialized_object):
        deserialized_object.save()
        # print deserialized_object.object
