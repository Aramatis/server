from django.core.management.base import BaseCommand
from django.core import serializers
from AndroidRequests.models import Report


class Command(BaseCommand):

    def handle(self, *args, **options):
        list_json = ['report.json',
                     'events_for_busstop.json',
                     'statistic_data_from_registration_busstop.json',
                     'events_for_busv2.json',
                     'statistic_data_from_registration_bus.json',
                     'busassignment.json',
                     'busv2.json']

        self.from_JSON(self.reports_cb,list_json)
        #self.from_JSON(self.polls_cb, "choices.json")
        

    def from_JSON(self, callback, filenames):
        for filename in filenames:
            with open(filename, 'r') as file:
                for deserialized_object in serializers.deserialize("json", file):
                    callback(deserialized_object)
            print "done"

    def reports_cb(self, deserialized_object):
        deserialized_object.save()
        #if not deserialized_object.object.imageName == "no image":
        #    print deserialized_object.object.imageName
        #print deserialized_object.object
        # print deserialized_object.object.pk
        # print deserialized_object.object.reports_text
        # print deserialized_object.object.pub_date
        #print "---"
        
