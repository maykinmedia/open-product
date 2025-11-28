from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import StateApps
from django.test import TransactionTestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from openproduct.accounts.models import User


class BaseApiTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)


class BaseMigrationTest(TransactionTestCase):
    app: str
    migrate_from: str  # The migration before the one we want to test
    migrate_to: str  # The migration we want to test

    setting_overrides: dict = {}

    old_app_state: StateApps
    app_state: StateApps

    def setUp(self) -> None:
        """
        Setup the migration test by reversing to `migrate_from` state,
        then applying the `migrate_to` state.
        """
        assert self.app is not None, "You must define the `app` attribute"
        assert self.migrate_from is not None, "You must define `migrate_from`"
        assert self.migrate_to is not None, "You must define `migrate_to`"

        # Step 1: Set up the MigrationExecutor
        executor = MigrationExecutor(connection)

        # Step 2: Reverse to the starting migration state
        migrate_from = [(self.app, self.migrate_from)]
        old_migrate_state = executor.migrate(migrate_from)

        self.old_app_state = old_migrate_state.apps

    def _perform_migration(self) -> None:
        migrate_to = [(self.app, self.migrate_to)]

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload the graph in case of dependency changes
        executor.migrate(migrate_to)

        self.apps = executor.loader.project_state(migrate_to).apps

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        # reset to latest migration
        call_command("migrate", verbosity=0, database=connection._alias)
