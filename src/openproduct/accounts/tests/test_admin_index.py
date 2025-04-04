from unittest import mock

from django.test import TestCase, override_settings

from .. import apps as accounts_apps


class DjangoAdminConfigTests(TestCase):

    @override_settings(INSTALLED_APPS=[])
    def test_update_admin_index_without_admin_index(self):
        with self.assertLogs(accounts_apps.__name__, level="WARNING") as cm:
            accounts_apps.update_admin_index(None)

        self.assertEqual(
            cm.output,
            [
                f"WARNING:{accounts_apps.__name__}:django_admin_index is not installed: skipping update_admin_index()"
            ],
        )

    @mock.patch("openproduct.accounts.apps.call_command")
    @override_settings(INSTALLED_APPS=["django_admin_index"])
    def test_update_admin_index_without_fixture(self, mock_call_command):
        mock_call_command.side_effect = ImportError()

        with self.assertLogs(accounts_apps.__name__, level="WARNING") as cm:
            accounts_apps.update_admin_index(None)

        self.assertEqual(
            cm.output,
            [
                f"WARNING:{accounts_apps.__name__}:Unable to load default_admin_index fixture (). You might have to regenerate the fixtures through 'bin/generate_admin_index_fixtures.sh'"
            ],
        )

    @mock.patch("openproduct.accounts.apps.call_command")
    @override_settings(INSTALLED_APPS=["django_admin_index"])
    def test_update_admin_index_with_fixture(self, mock_call_command):
        with self.assertLogs(accounts_apps.__name__, level="INFO") as cm:
            accounts_apps.update_admin_index(None)

        self.assertEqual(mock_call_command.call_count, 1)

        self.assertEqual(
            cm.output,
            [f"INFO:{accounts_apps.__name__}:Loaded django-admin-index fixture:\n"],
        )
