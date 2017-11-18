from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from gtfs.loaders.LoaderFactory import LoaderFactory

import os


class Command(BaseCommand):
    help = 'load gtfs based on version'

    def __init__(self):
        super(Command, self).__init__()

        app_name = 'gtfs'
        log_folder_name = 'log'
        self.log_file_name = '%s.log' % timezone.now().strftime('%Y%m%d_%H%M%S')
        data_folder_name = 'data'

        self.file_path = os.path.join(settings.BASE_DIR, app_name, data_folder_name)
        self.log_path = os.path.join(settings.BASE_DIR, app_name, log_folder_name)
        
        self.gtfs_version = None
        self.models = []

    def add_arguments(self, parser):
        parser.add_argument('gtfs_version', help='gtfs version to load')
        parser.add_argument('models', nargs='+',
                            help='models to update. possible values : '
                                 'stop route routelocation routestopdistance routebystop shape')
        parser.add_argument('--logfilename', default=None, help='name of log file generated in the execution')

    def handle(self, *args, **options):
        self.gtfs_version = options['gtfs_version']
        self.models = options['models']
        log_file_name = options['logfilename']

        if log_file_name:
            log_file = os.path.join(self.log_path, log_file_name)
        else:
            log_file = os.path.join(self.log_path, self.log_file_name)

        try:
            factory = LoaderFactory()
            with open(log_file, 'w+') as log:
                for model in self.models:
                    path = self.get_path_file(model)
                    with open(path, 'r') as csv_file:
                        # skip header
                        csv_file.next()
                        loader = factory.getModelLoader(model)(csv_file, log, self.gtfs_version)
                        loader.load()
                    self.stdout.write(self.style.SUCCESS("%s data copied successfully." % model))
        except Exception as e:
            raise CommandError(str(e))

    def get_path_file(self, model_name):
        """ get path of file to upload """
        
        if model_name == 'stop':
            file_name = 'busstop.csv'
        elif model_name == 'route':
            file_name = 'services.csv'
        elif model_name == 'routelocation':
            file_name = 'servicelocation.csv'
        elif model_name == 'routestopdistance':
            file_name = 'servicestopdistance.csv'
        elif model_name == 'routebystop':
            file_name = 'servicesbybusstop.csv'
        elif model_name == 'shape':
            file_name = 'shape.csv'
        else:
            raise ValueError('model name does not match with any valid model name: '
                             'stop route routelocation routestopdistance routebystop shape')
            
        return os.path.join(self.file_path, self.gtfs_version, file_name)
