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
        self.file_path = os.path.join(settings.BASE_DIR, app_name, data_folder_name)
        
        self.gtfs_version = None

    def add_arguments(self, parser):
        parser.add_argument('gtfs_version', help='gtfs version to load. For instance: v1.2')
        parser.add_argument('--no-input', default=None, action='store_true',
                            help='assume user says yes for every prompt')

    def handle(self, *args, **options):
        self.gtfs_version = options['gtfs_version']
        no_input = options['no_input']

        try:
            """ it generates a folder with the gtfs version data """
            directory = os.path.join(self.file_path, self.gtfs_version)
            try:
                self.stdout.write(self.style.NOTICE("creating directory '%s'" % directory))
                os.mkdir(directory)
            except OSError:
                self.stdout.write(self.style.NOTICE("directory '%s' already exists..." % directory))

            for fileName, webFileName in self.getFileNames():
                filePath = os.path.join(self.file_path, self.gtfs_version, fileName)

                if os.path.isfile(filePath):
                    message = "file '%s' exists. Do you want to replace it?(yes/no)" % fileName
                    if no_input:
                        answer = 'yes'
                    else:
                        answer = raw_input(message)
                    if answer.lower() in ['yes', 'y']:
                        self.download_file(fileName, webFileName, filePath)
                    else:
                        self.stdout.write(self.style.NOTICE("file '%s' skipped" % fileName))
                else:
                    self.download_file(fileName, webFileName, filePath)
        except Exception as e:
            raise CommandError(str(e))

    def download_file(self, fileName, webFileName, filePath):
        """ download file from GTFSProcessing repository """

        url = "%s/%s" % (self.URL_PREFIX, webFileName)
        self.stdout.write(self.style.NOTICE("downloading ... %s" % url))
        self.downloader.retrieve(url, filePath)
        self.stdout.write(self.style.SUCCESS("file '%s' updated" % fileName))

    def getFileNames(self):
        """  """
        FILE_NAMES = [
            # syntax: (localName, webName)
            ('busstop.csv', 'busstop{}.csv'.format(self.gtfs_version)),
            ('services.csv', 'services{}.csv'.format(self.gtfs_version)),
            ('servicesbybusstop.csv', 'servicesbybusstop{}.csv'.format(self.gtfs_version)),
            ('servicestopdistance.csv', 'servicestopdistance{}.csv'.format(self.gtfs_version)),
            ('servicelocation.csv', 'servicelocation{}.csv'.format(self.gtfs_version))
        ]

        return FILE_NAMES