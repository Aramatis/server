from django.apps import apps
from django.test import TestCase
from django.utils import timezone

from django.db.migrations.executor import MigrationExecutor
from django.db import connection

import uuid


class TestMigrations(TestCase):
    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass


class Migration42Test(TestMigrations):
    migrate_from = '0041_transappuser_timecreation'
    migrate_to = '0042_fixed_timecreation_20171115_1319'

    def setUpBeforeMigration(self, apps):
        self.Token = apps.get_model('AndroidRequests', 'token')
        ScoreHistory = apps.get_model('AndroidRequests', 'scorehistory')
        ScoreEvent = apps.get_model('AndroidRequests', 'scoreEvent')
        Bus = apps.get_model('AndroidRequests', 'busv2')
        Busassignment = apps.get_model('AndroidRequests', 'busassignment')
        Level = apps.get_model('AndroidRequests', 'level')
        TranSappUser = apps.get_model('AndroidRequests', 'transappuser')
        PoseTrajectoryOfToken = apps.get_model('AndroidRequests', 'poseintrajectoryoftoken')

        level = Level.objects.create(position=1)
        self.tranSappUser = TranSappUser.objects.create(phoneId=uuid.uuid4(), sessionToken=uuid.uuid4(), level=level,
                                                        globalPosition=1)
        bus = Bus.objects.create(uuid=uuid.uuid4())
        bus_assignment = Busassignment.objects.create(uuid=bus)

        self.uuidToken = uuid.uuid4()
        token = self.Token.objects.create(token=self.uuidToken, phoneId=uuid.uuid4(), busassignment=bus_assignment)

        score_event_ob = ScoreEvent.objects.create()
        ScoreHistory.objects.create(tranSappUser=self.tranSappUser, scoreEvent=score_event_ob,
                                    timeCreation=timezone.now(), score=10, meta="asd %s 12312" % self.uuidToken)

        self.timeCreation = timezone.now()
        PoseTrajectoryOfToken.objects.create(token=token, timeStamp=self.timeCreation, longitude=1, latitude=1)

    def test_checkMigration(self):
        """ at this point migration was executed and now we have to check asserts """
        token_obj = self.Token.objects.get(token=self.uuidToken)
        self.assertEquals(token_obj.timeCreation, self.timeCreation)
        self.assertEquals(token_obj.tranSappUser_id, self.tranSappUser.id)
