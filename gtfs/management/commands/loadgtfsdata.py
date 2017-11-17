from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from Loaders.LoaderFactory import LoaderFactory

import os


class Command(BaseCommand):
    help = 'load gtfs based on version'

    def __init__(self):
        super(Command, self).__init__()

        self.app_name = 'gtfs'
        self.log_folder_name = 'log'
        self.log_file_name = '%s.log' % timezone.now().strftime('%Y%m%d%H%M%S')
        self.data_folder_name = 'data'

        self.gtfs_version = None
        self.models = []

    def add_arguments(self, parser):
        parser.add_argument('gtfs_version', type=int, help='gtfs version to load')
        parser.add_argument('models', nargs='+',
                            help='models to update. possible values : '
                                 'stop route routelocation routestopdistance routebystop shape')

    def handle(self, *args, **options):
        self.gtfs_version = options['gtfs_version']
        self.models = options['models']

        log_file = os.path.join(settings.BASE_DIR, self.app_name, self.log_folder_name, self.log_file_name)
        try:
            factory = LoaderFactory()
            with open(log_file, 'w+') as log:
                for model in self.models:
                    csv = open(self.get_path_file(model), 'r')
                    # skip header
                    csv.next()
                    loader = factory.getModelLoader(model)(csv, log, self.gtfs_version)
                    loader.load()
                    csv.close()
        except Exception as e:
            raise CommandError(str(e))

    def get_path_file(self, model_name):
        """ get path of file to upload """

        file_path = os.path.join(settings.BASE_DIR, self.app_name, self.gtfs_version, self.data_folder_name)
        
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
            
        return os.path.join(file_path, file_name)
