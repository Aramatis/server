# -*- coding: utf-8 -*-
from django.test import TestCase, TransactionTestCase
from django.core.management import call_command, CommandError
from django.conf import settings

from io import BytesIO

from gtfs.loaders.LoaderFactory import LoaderFactory

import os


class CommandsTest(TransactionTestCase):

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


class LoaderFactoryTest(TestCase):

    def test_loader_factory_with_wrong_model(self):
        """ tray to get loader that not exist """
        non_exist_model = "asdad"
        self.assertRaises(ValueError, LoaderFactory().getModelLoader, non_exist_model)
