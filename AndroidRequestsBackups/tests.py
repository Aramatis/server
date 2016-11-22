from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO
from AndroidRequestsBackups.jobs import *

# Create your tests here.

class appTest(TestCase):

    def setUp(self):
        """ set variables in settings.py to test commands """

    def test_command_output(self):
        pass
        #out = StringIO()
        #call_command('visualization_backup_dump', stdout=out)
        complete_dump()
        partial_dump()
        #self.assertIn('Expected output', out.getvalue())

    def test_command_output2(self):
        pass
        #out = StringIO()
        #call_command('visualization_backup_loaddata', stdout=out)

        #self.assertIn('Expected output', out.getvalue())

        complete_loaddata()
        partial_loaddata()
