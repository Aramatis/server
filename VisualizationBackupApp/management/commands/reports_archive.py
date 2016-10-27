from django.core.management.base import BaseCommand
from django.core import serializers
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.archive_reports()



    # ----------------------------------------------------------------------------
    # QUERIES
    # ----------------------------------------------------------------------------
    def get_reports_query(self):
        from AndroidRequests.models import Report
        return Report.objects.filter(timeStamp__gt = self.get_past_date(5000))
  

    # ----------------------------------------------------------------------------
    # PROCESSING
    # ----------------------------------------------------------------------------
    def archive_reports(self):
        reports = self.get_reports_query()

        print "writing images list"
        with open("/tmp/report_images.txt", 'w') as file:
            for report in reports:
                file.write(report.imageName + "\n")

        self.to_JSON(reports, "/tmp/reports.json")


    # ----------------------------------------------------------------------------
    # MISC
    # ----------------------------------------------------------------------------        
    def to_JSON(self, query, filename):
        print "writing json file: " + filename
        JSONSerializer = serializers.get_serializer("json")
        json_serializer = JSONSerializer()
        with open(filename, 'w') as file:
            json_serializer.serialize(query, stream=file)
    

    def get_past_date(self, hours):
        return (timezone.now() - timedelta(hours=hours))