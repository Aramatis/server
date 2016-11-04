from django.core.management.base import BaseCommand
from django.core import serializers
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):

    help = 'Creates JSON backup files for AndroidRequests.{Reports,  \
            EventForBus, EventForBusStop}. Files are created within \
            the current folder'

    # ----------------------------------------------------------------------------
    # CONIGURATION
    # ----------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
    
        # configuration
        self.delta_days    = 100
        self.delta_hours   = 0
        self.delta_minutes = 5
        self.delta_seconds = 0



    # ----------------------------------------------------------------------------
    # COMMAND
    # ----------------------------------------------------------------------------    
    def handle(self, *args, **options):
        self.archive_reports()
        self.archive_events_for_busstop()
        self.archive_events_for_busv2()



    # ----------------------------------------------------------------------------
    # PROCESSING
    # ----------------------------------------------------------------------------
    def archive_reports(self):
        query = self.get_reports_query()
        print "writing images list"
        with open("report_images.txt", 'w') as file:
            for report in query:
                # meanwhile!: check for string length
                # this should be removed when imageName changes to null 
                # in the app
                if report.imageName is not None and len(report.imageName) > 10:
                    file.write(report.imageName + "\n")
        self.to_JSON(query, "reports.json")



    def archive_events_for_busv2(self):
        query = self.get_events_for_busv2_query()

        # new primary keys
        event_ids = []
        busassignment_ids = []
        for event in query:
            event_ids.append(event.id)
            busassignment_ids.append(event.busassignment_id)
        self.to_JSON(query, "events_for_busv2.json")
        del query


        # related stats
        final_stats = []
        query_statistic = self.get_statistic_data_from_registration_bus_query()
        for stat in query_statistic:
            if stat.reportOfEvent_id in event_ids:
                final_stats.append(stat)
        self.to_JSON(final_stats, "statistic_data_from_registration_bus.json")
        del final_stats
        del query_statistic

        # related assignments
        required_bus_uuids = []
        final_assignments = []
        query_assignments = self.get_busassignment_query()
        for assignment in query_assignments:
            if assignment.id in busassignment_ids:
                required_bus_uuids.append(assignment.uuid_id)
                final_assignments.append(assignment)
        self.to_JSON(final_assignments, "busassignment.json")
        del query_assignments
        del final_assignments

        # related buses
        final_buses = []
        query_buses = self.get_busv2_query()
        for bus in query_buses:
            if bus.id in required_bus_uuids:
                final_buses.append(bus)
        self.to_JSON(final_buses, "busv2.json")
        del final_buses
        del query_buses



    def archive_events_for_busstop(self):
        query = self.get_event_for_busstop_query()
        self.to_JSON(query, "events_for_busstop.json")

        # new primary keys
        required_ids = []
        for event in query:
            required_ids.append(event.id)

        # related rows
        final_query = []
        query_statistic = self.get_statistic_data_from_registration_busstop_query()
        for stat in query_statistic:
            if stat.reportOfEvent_id in required_ids:
                final_query.append(stat)

        self.to_JSON(final_query, "statistic_data_from_registration_busstop.json")



    # ----------------------------------------------------------------------------
    # QUERIES
    # ----------------------------------------------------------------------------
    def get_reports_query(self):
        from AndroidRequests.models import Report
        return Report.objects.filter(timeStamp__gt = self.get_past_date())

    def get_events_for_busv2_query(self):
        from AndroidRequests.models import EventForBusv2
        return EventForBusv2.objects.filter(timeStamp__gt = self.get_past_date())

    def get_busv2_query(self):
        from AndroidRequests.models import Busv2
        return Busv2.objects.all()

    def get_busassignment_query(self):
        from AndroidRequests.models import Busassignment
        return Busassignment.objects.all()

    def get_event_for_busstop_query(self):
        from AndroidRequests.models import EventForBusStop
        return EventForBusStop.objects.filter(timeStamp__gt = self.get_past_date())

    def get_statistic_data_from_registration_busstop_query(self):
        from AndroidRequests.models import StadisticDataFromRegistrationBusStop
        return StadisticDataFromRegistrationBusStop.objects.filter(timeStamp__gt = self.get_past_date())

    def get_statistic_data_from_registration_bus_query(self):
        from AndroidRequests.models import StadisticDataFromRegistrationBus
        return StadisticDataFromRegistrationBus.objects.filter(timeStamp__gt = self.get_past_date())
        


    # ----------------------------------------------------------------------------
    # MISC
    # ----------------------------------------------------------------------------        
    def to_JSON(self, query, filename):
        print "writing json file: " + filename
        JSONSerializer = serializers.get_serializer("json")
        json_serializer = JSONSerializer()
        with open(filename, 'w') as file:
            json_serializer.serialize(query, stream=file)


    def get_past_date(self):
        return (
            timezone.now() - 
            timedelta(
                days=self.delta_days,
                hours=self.delta_hours,
                minutes=self.delta_minutes
            )
        )

