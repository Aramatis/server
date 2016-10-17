from django.core.management.base import BaseCommand
from AndroidRequests.models import Report
from django.utils import timezone
from datetime import timedelta



class Command(BaseCommand):

    def handle(self, *args, **options):
    	a = Report.objects.filter(timeStamp__gt = (timezone.now() - timedelta(hours=5)))
    	print a