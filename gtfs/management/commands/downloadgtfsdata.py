from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import urllib
import os


class Command(BaseCommand):
    help = 'download gtfs based on version from https://github.com/InspectorIncognito/GTFSProcessing'

    downloader = urllib.URLopener()
    URL_PREFIX = 'https://raw.githubusercontent.com/InspectorIncognito/GTFSProcessing/master/procesaGTFS/x64/Release'

    def __init__(self):
        super(Command, self).__init__()

        app_name = 'gtfs'
        data_folder_name = 'data'
        self.phone_folder_data = 'phone'
        self.server_folder_data = 'server'
        self.file_path = os.path.join(settings.BASE_DIR, app_name, data_folder_name)
        
        self.gtfs_version = None

    def add_arguments(self, parser):
        parser.add_argument('gtfs_version', help='gtfs version to load. For instance: v1.2')
        parser.add_argument('--not-input', default=None, action='store_true',
                            help='assume user says yes for every prompt')

    def handle(self, *args, **options):
        self.gtfs_version = options['gtfs_version']
        not_input = options['not_input']

        try:
            """ it generates a folder with the gtfs version data """
            directory = os.path.join(self.file_path, self.gtfs_version)
            phone_directory = os.path.join(directory, self.phone_folder_data)
            server_directory = os.path.join(directory, self.server_folder_data)
            for file_directory in [phone_directory, server_directory]:
                try:
                    self.stdout.write(self.style.NOTICE("creating directory '%s'" % file_directory))
                    os.makedirs(file_directory)
                except OSError:
                    self.stdout.write(self.style.NOTICE("FAIL! directory '%s' already exists..." % file_directory))

            for file_name, web_file_name in self.get_server_file_names():
                self.process_file(server_directory, file_name, web_file_name, not_input)
            for file_name, web_file_name in self.get_phone_file_names():
                self.process_file(phone_directory, file_name, web_file_name, not_input)
        except Exception as e:
            raise CommandError(str(e))

    def process_file(self, path, file_name, web_file_name, option_not_input):
        file_path = os.path.join(path, file_name)

        if os.path.isfile(file_path):
            message = "file '%s' exists. Do you want to replace it?(yes/no)" % file_name
            if option_not_input:
                answer = 'yes'
            else:
                answer = raw_input(message)
            if answer.lower() in ['yes', 'y']:
                self.download_file(file_name, web_file_name, file_path)
            else:
                self.stdout.write(self.style.NOTICE("file '%s' skipped" % file_name))
        else:
            self.download_file(file_name, web_file_name, file_path)

    def download_file(self, fileName, webFileName, filePath):
        """ download file from GTFSProcessing repository """

        url = "%s/%s" % (self.URL_PREFIX, webFileName)
        self.stdout.write(self.style.NOTICE("downloading ... %s" % url))
        self.downloader.retrieve(url, filePath)
        self.stdout.write(self.style.SUCCESS("file '%s' updated" % fileName))

    def get_server_file_names(self):
        """ server files """
        file_names = [
            # syntax: (localName, webName)
            ('busstop.csv', 'busstop{}.csv'.format(self.gtfs_version)),
            ('services.csv', 'services{}.csv'.format(self.gtfs_version)),
            ('servicesbybusstop.csv', 'servicesbybusstop{}.csv'.format(self.gtfs_version)),
            ('servicestopdistance.csv', 'servicestopdistance{}.csv'.format(self.gtfs_version)),
            ('servicelocation.csv', 'servicelocation{}.csv'.format(self.gtfs_version))
        ]

        return file_names


    def get_phone_file_names(self):
        """ phone files """
        file_names = [
            # syntax: (localName, webName)
            ('busstop.csv', 'Android_busstops{}.csv'.format(self.gtfs_version)),
            ('grid.csv', 'Android_grid{}.csv'.format(self.gtfs_version)),
            ('loadfarepoint.csv', 'Android_puntoscarga{}.csv'.format(self.gtfs_version)),
            ('shape.csv', 'Android_routes{}.csv'.format(self.gtfs_version)),
            ('route.csv', 'Android_services{}.csv'.format(self.gtfs_version))
        ]

        return file_names