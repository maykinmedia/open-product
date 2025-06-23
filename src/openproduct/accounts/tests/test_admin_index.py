from unittest import mock

from django.test import TestCase, override_settings

from .. import apps as accounts_apps


class DjangoAdminConfigTests(TestCase):
    @override_settings(INSTALLED_APPS=[])
    def test_update_admin_index_without_admin_index(self):
        with self.assertLogs(accounts_apps.__name__, level="WARNING") as cm:
            accounts_apps.update_admin_index(None)

        self.assertIn(
            "event': 'django_admin_index_not_installed_skipping_update_admin_index",
            cm.output[0],
        )

    @mock.patch("openproduct.accounts.apps.call_command")
    @override_settings(INSTALLED_APPS=["django_admin_index"])
    def test_update_admin_index_without_fixture(self, mock_call_command):
        mock_call_command.side_effect = ImportError()

        with self.assertLogs(accounts_apps.__name__, level="WARNING") as cm:
            accounts_apps.update_admin_index(None)

        self.assertIn(
            "event': 'unable_to_load_default_admin_index_fixture_might_need_to_regenerate",
            cm.output[0],
        )

    @mock.patch("openproduct.accounts.apps.call_command")
    @override_settings(INSTALLED_APPS=["django_admin_index"])
    def test_update_admin_index_with_fixture(self, mock_call_command):
        with self.assertLogs(accounts_apps.__name__, level="INFO") as cm:
            accounts_apps.update_admin_index(None)

        self.assertEqual(mock_call_command.call_count, 1)

        self.assertIn(
            "event': 'loaded_django_admin_index_fixture",
            cm.output[0],
        )
