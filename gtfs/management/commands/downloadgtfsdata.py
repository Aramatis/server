from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import urllib
import os


class Command(BaseCommand):
    help = 'download gtfs based on version from https://github.com/InspectorIncognito/GTFSProcessing'

    URL_PREFIX = 'https://raw.githubusercontent.com/InspectorIncognito/GTFSProcessing/master/procesaGTFS/x64/Release'

    def __init__(self):
        super(Command, self).__init__()

        app_name = 'gtfs'
        data_folder_name = 'data'
        self.file_path = os.path.join(settings.BASE_DIR, app_name, data_folder_name)
        
        self.gtfs_version = None

    def add_arguments(self, parser):
        parser.add_argument('gtfs_version', help='gtfs version to load. For instance: v1.2')

    def handle(self, *args, **options):
        self.gtfs_version = options['gtfs_version']

        try:
            """ generate a folder with the gtfs version data """
            FILE_NAMES = [
                # (localName, webName)
                ('busstop.csv', 'busstop{}.csv'.format(self.gtfs_version)),
                ('services.csv', 'services{}.csv'.format(self.gtfs_version)),
                ('servicesbybusstop.csv', 'servicesbybusstop{}.csv'.format(self.gtfs_version)),
                ('servicestopdistance.csv', 'servicestopdistance{}.csv'.format(self.gtfs_version)),
                ('servicelocation.csv', 'servicelocation{}.csv'.format(self.gtfs_version))
            ]

            directory = os.path.join(self.file_path, self.gtfs_version)
            try:
                self.stdout.write(self.style.NOTICE("creating directory '%s'" % directory))
                os.mkdir(directory)
            except OSError:
                self.stdout.write(self.style.NOTICE("directory '%s' already exists..." % directory))

            for fileName, webFileName in FILE_NAMES:
                filePath = os.path.join(self.file_path, self.gtfs_version, fileName)

                if os.path.isfile(filePath):
                    message = "file '{}' exists. Do you want to replace it?(yes/no)".format(fileName)
                    answer = raw_input(message)
                    if answer.lower() in ['yes', 'y']:
                        self.downloadFile(fileName, webFileName, filePath)
                    else:
                        print "file '{}' skipped".format(fileName)
                else:
                    self.downloadFile(fileName, webFileName, filePath)
        except Exception as e:
            raise CommandError(str(e))

    def downloadFile(self, fileName, webFileName, filePath):
        """ download file from GTFSProcessing repository """
        downloader = urllib.URLopener()

        url = "%s/%s" % (self.URL_PREFIX, webFileName)
        self.stdout.write(self.style.NOTICE("downloading ... %s" % url))
        downloader.retrieve(url, filePath)
        self.stdout.write(self.style.SUCCESS("file '%s' updated" % fileName))
