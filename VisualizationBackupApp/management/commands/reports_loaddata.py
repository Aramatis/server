from django.core.management.base import BaseCommand
from django.core import serializers


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.from_JSON(self.reports_cb, "reports.json")
        #self.from_JSON(self.polls_cb, "choices.json")
        

    def from_JSON(self, callback, filename):
        with open(filename, 'r') as file:
            for deserialized_object in serializers.deserialize("json", file):
                callback(deserialized_object)
        print "done"


    from AndroidRequests.models import Report
    def reports_cb(self, deserialized_object):
        #deserialized_object.save()
        if not deserialized_object.object.imageName == "no image":
            print deserialized_object.object.imageName
        #print deserialized_object.object
        # print deserialized_object.object.pk
        # print deserialized_object.object.reports_text
        # print deserialized_object.object.pub_date
        #print "---"
        
