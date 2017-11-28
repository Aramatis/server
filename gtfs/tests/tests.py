# -*- coding: utf-8 -*-
from django.test import TestCase, TransactionTestCase, Client
from django.core.management import call_command, CommandError
from django.conf import settings
from django.urls import reverse

from io import BytesIO
from mock import Mock

from gtfs.loaders.LoaderFactory import LoaderFactory
from gtfs.management.commands import downloadgtfsdata

import os
import shutil
import urllib
import json


class CommandLoadgtfsdataTest(TransactionTestCase):

    def setUp(self):
        self.command = 'loadgtfsdata'
        self.gtfs_version = 'test'

        self.log_file_name = 'log.log'
        self.log_path = os.path.join(settings.BASE_DIR, 'gtfs', 'log', self.log_file_name)

    def tearDown(self):
        """ delete log file """
        if os.path.isfile(self.log_path):
            os.remove(self.log_path)

    def test_command_loadgtfsdata_too_few_arguments(self):
        """ test command loadgtfsdata. Raise error CommandError. too few arguments"""
        self.assertRaises(CommandError, call_command, self.command)
        self.assertRaises(CommandError, call_command, self.command, self.gtfs_version)

    def test_command_loadgtfsdata_with_2_models_output(self):
        """ test command loadgtfsdata. Raise error CommandError. too few arguments"""
        out = BytesIO()
        model = ['stop', 'route']
        call_command(self.command, self.gtfs_version, model[0], model[1], '--logfilename',
                     self.log_file_name, stdout=out)
        self.assertIn(model[0], out.getvalue())
        self.assertIn(model[1], out.getvalue())

    def test_command_loadgtfsdata_output(self):
        """ test command loadgtfsdata. Raise error CommandError. too few arguments"""
        out = BytesIO()
        models = ['stop', 'route', 'routelocation', 'routestopdistance', 'routebystop', 'shape']
        for model in models:
            call_command(self.command, self.gtfs_version, model, '--logfilename', self.log_file_name, stdout=out)
            self.assertIn(model, out.getvalue())

            if os.path.isfile(self.log_path):
                with open(self.log_path) as log_file:
                    self.assertNotEqual(log_file.read(), "")


class CommandDownloadgtfsdataTest(TransactionTestCase):
    """ test command downloadgtfsdata """

    def setUp(self):
        self.command = 'downloadgtfsdata'
        self.gtfs_version = 'test2'
        self.server_data_path = os.path.join(settings.BASE_DIR, 'gtfs', 'data', self.gtfs_version, 'server')

    def tearDown(self):
        """ delete log file """
        if os.path.isdir(self.server_data_path):
            shutil.rmtree(self.server_data_path)

    def test_command_too_few_arguments(self):
        """ Raise error CommandError. too few arguments"""
        self.assertRaises(CommandError, call_command, self.command)
        self.assertRaises(CommandError, call_command, self.command, self.gtfs_version)

    def test_command_directory_does_not_exist(self):
        """ download data """
        out = BytesIO()
        command_obj = downloadgtfsdata.Command()
        urllib_mock = Mock(spec=urllib.URLopener())
        urllib_mock.configure_mock(**{"retrieve.return_value": True})
        command_obj.downloader = urllib_mock

        call_command(command_obj, self.gtfs_version, stdout=out)
        self.assertIn("creating directory", out.getvalue())
        self.assertIn("file 'busstop.csv' updated", out.getvalue())
        self.assertIn("file 'services.csv' updated", out.getvalue())
        self.assertIn("file 'servicesbybusstop.csv' updated", out.getvalue())
        self.assertIn("file 'servicestopdistance.csv' updated", out.getvalue())
        self.assertIn("file 'servicelocation.csv' updated", out.getvalue())

    def test_command_directory_exists(self):
        """ download data """
        out = BytesIO()
        command_obj = downloadgtfsdata.Command()
        urllib_mock = Mock(spec=urllib.URLopener())
        urllib_mock.configure_mock(**{"retrieve.return_value": True})
        command_obj.downloader = urllib_mock

        # create directory
        os.makedirs(self.server_data_path)
        # and file exists
        open(os.path.join(self.server_data_path, "busstop.csv"), 'w').close()

        call_command(command_obj, self.gtfs_version, '--not-input', stdout=out)
        self.assertIn(" already exists", out.getvalue())
        self.assertIn("file 'busstop.csv' updated", out.getvalue())
        self.assertIn("file 'services.csv' updated", out.getvalue())
        self.assertIn("file 'servicesbybusstop.csv' updated", out.getvalue())
        self.assertIn("file 'servicestopdistance.csv' updated", out.getvalue())
        self.assertIn("file 'servicelocation.csv' updated", out.getvalue())


class LoaderFactoryTest(TestCase):

    def test_loader_factory_with_wrong_model(self):
        """ tray to get loader that not exist """
        non_exist_model = "asdad"
        self.assertRaises(ValueError, LoaderFactory().getModelLoader, non_exist_model)


class GetGTFSVersionTest(TestCase):

    def test_get_gtfs_version(self):
        client = Client()
        url = reverse("gtfs:version")
        json_response = client.get(url)

        self.assertEquals(json_response.status_code, 200)

        json_response = json.loads(json_response.content)
        self.assertEquals(json_response["version"], settings.GTFS_VERSION)
