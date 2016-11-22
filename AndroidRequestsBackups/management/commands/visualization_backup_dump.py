from django.core.management.base import BaseCommand
from django.core import serializers
from django.utils import timezone
from datetime import timedelta
import time


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
        self.delta_minutes = 0
        self.report_images_filename = "dump_report_images.txt"


    # ----------------------------------------------------------------------------
    # COMMAND
    # ----------------------------------------------------------------------------
    def add_arguments(self, parser):
        parser.add_argument('minutes', type=int)


    def handle(self, *args, **options):
        if options['minutes']:
            self.delta_minutes = options['minutes']

        print("Partial dump for newest data - (%d min)" % (self.delta_minutes))
        start_time = time.time()
        start_time_str = time.strftime("%b %d %Y %H:%M:%S", time.localtime(start_time))
        print("... started ... at: %s" % start_time_str)
        time.sleep(1)
        self.archive_reports()
        self.archive_events_for_busstop()
        self.archive_events_for_busv2()
        finish_time = time.time()
        elapsed_time = finish_time - start_time
        finish_time_str = time.strftime("%b %d %Y %H:%M:%S", time.localtime(finish_time))
        print("... finished ... at %s ... elapsed: %d [s]" % (finish_time_str, elapsed_time))


    # ----------------------------------------------------------------------------
    # PROCESSING
    # ----------------------------------------------------------------------------
    def archive_reports(self):
        [query, modelname] = self.get_reports_query()
        print("writing images list")
        with open(self.report_images_filename, 'w+') as file:
            for report in query:
                # meanwhile!: check for string length
                # this should be removed when imageName changes to null 
                # in the app
                if report.imageName is not None and len(report.imageName) > 10:
                    file.write(report.imageName + "\n")
        self.to_JSON(query, modelname)



    def archive_events_for_busv2(self):
        [query, events_busv2_modelname] = self.get_events_for_busv2_query()

        # new primary keys
        event_ids = []
        busassignment_ids = []
        for event in query:
            event_ids.append(event.id)
            busassignment_ids.append(event.busassignment_id)
        self.to_JSON(query, events_busv2_modelname)
        del query


        # related stats
        final_stats = []
        [query_statistic, sdfrb_modelname] = self.get_statistic_data_from_registration_bus_query()
        for stat in query_statistic:
            if stat.reportOfEvent_id in event_ids:
                final_stats.append(stat)
        self.to_JSON(final_stats, sdfrb_modelname)
        del final_stats
        del query_statistic

        # related assignments
        required_bus_uuids = []
        final_assignments = []
        [query_assignments, busassignment_modelname] = self.get_busassignment_query()
        for assignment in query_assignments:
            if assignment.id in busassignment_ids:
                required_bus_uuids.append(assignment.uuid_id)
                final_assignments.append(assignment)
        self.to_JSON(final_assignments, busassignment_modelname)
        del query_assignments
        del final_assignments

        # related buses
        final_buses = []
        [query_buses, busv2_modelname] = self.get_busv2_query()
        for bus in query_buses:
            if bus.id in required_bus_uuids:
                final_buses.append(bus)
        self.to_JSON(final_buses, busv2_modelname)
        del final_buses
        del query_buses



    def archive_events_for_busstop(self):
        [query, busstop_modelname] = self.get_event_for_busstop_query()
        self.to_JSON(query, busstop_modelname)

        # new primary keys
        required_ids = []
        for event in query:
            required_ids.append(event.id)

        # related rows
        final_query = []
        [query_statistic, sdfrbs_modelname] = self.get_statistic_data_from_registration_busstop_query()
        for stat in query_statistic:
            if stat.reportOfEvent_id in required_ids:
                final_query.append(stat)

        self.to_JSON(final_query, sdfrbs_modelname)



    # ----------------------------------------------------------------------------
    # QUERIES
    # ----------------------------------------------------------------------------
    def get_reports_query(self):
        from AndroidRequests.models import Report
        return [Report.objects.filter(timeStamp__gt=self.get_past_date()), Report.__name__]

    def get_events_for_busv2_query(self):
        from AndroidRequests.models import EventForBusv2
        return [EventForBusv2.objects.filter(timeStamp__gt=self.get_past_date()), EventForBusv2.__name__]

    def get_busv2_query(self):
        from AndroidRequests.models import Busv2
        return [Busv2.objects.all(), Busv2.__name__]

    def get_busassignment_query(self):
        from AndroidRequests.models import Busassignment
        return [Busassignment.objects.all(), Busassignment.__name__]

    def get_event_for_busstop_query(self):
        from AndroidRequests.models import EventForBusStop
        return [EventForBusStop.objects.filter(timeStamp__gt=self.get_past_date()), EventForBusStop.__name__]

    def get_statistic_data_from_registration_busstop_query(self):
        from AndroidRequests.models import StadisticDataFromRegistrationBusStop
        return [StadisticDataFromRegistrationBusStop.objects.filter(timeStamp__gt=self.get_past_date()), StadisticDataFromRegistrationBusStop.__name__]

    def get_statistic_data_from_registration_bus_query(self):
        from AndroidRequests.models import StadisticDataFromRegistrationBus
        return [StadisticDataFromRegistrationBus.objects.filter(timeStamp__gt=self.get_past_date()), StadisticDataFromRegistrationBus.__name__]
    

    # ----------------------------------------------------------------------------
    # MISC
    # ----------------------------------------------------------------------------
    
    def to_JSON(self, query, modelname):
        filename = "dump_" + modelname + ".json"
        print("writing %d '%s' objects to json file %s" % (len(query), modelname, filename))
        JSONSerializer = serializers.get_serializer("json")
        json_serializer = JSONSerializer()
        with open(filename, 'w+') as file:
            json_serializer.serialize(query, stream=file)


    def get_past_date(self):
        return (
            timezone.now() - 
            timedelta(
                days=0,
                minutes=self.delta_minutes
            )
        )

