import os
from io import StringIO

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings

from ..models import User


class CreateInitialSuperuserTests(TestCase):
    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_create_initial_superuser_command(self):
        call_command(
            "createinitialsuperuser",
            "--generate-password",
            "--email-password-reset",
            username="maykin",
            email="support@maykinmedia.nl",
            stdout=StringIO(),
        )
        user = User.objects.get()

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertEqual(
            sent_mail.subject,
            f"Your admin user for {settings.PROJECT_NAME} (example.com)",
        )
        self.assertEqual(sent_mail.recipients(), ["support@maykinmedia.nl"])

    @override_settings(ALLOWED_HOSTS=[])
    def test_create_initial_superuser_command_allowed_hosts_empty(self):
        call_command(
            "createinitialsuperuser",
            "--generate-password",
            "--email-password-reset",
            username="maykin",
            email="support@maykinmedia.nl",
            stdout=StringIO(),
        )
        user = User.objects.get()

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertEqual(
            sent_mail.subject,
            f"Your admin user for {settings.PROJECT_NAME} (unknown url)",
        )
        self.assertEqual(sent_mail.recipients(), ["support@maykinmedia.nl"])

    def test_create_from_cli(self):
        call_command(
            "createinitialsuperuser",
            "--username=admin",
            "--password=admin",
            "--email=admin@example.com",
            "--no-input",
            stdout=StringIO(),
        )

        user = User.objects.get()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("admin"))

    def test_command_noop_if_user_exists(self):
        User.objects.create(username="admin")

        call_command(
            "createinitialsuperuser",
            "--username=admin",
            "--password=admin",
            "--email=admin@example.com",
            "--no-input",
            stdout=StringIO(),
        )

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "")
        self.assertFalse(user.check_password("admin"))

    def test_password_from_env(self):
        os.environ["OPENPRODUCT_SUPERUSER_PASSWORD"] = "admin"

        def reset_env():
            del os.environ["OPENPRODUCT_SUPERUSER_PASSWORD"]

        self.addCleanup(reset_env)

        call_command(
            "createinitialsuperuser",
            "--username=admin",
            "--email=admin@example.com",
            "--no-input",
            stdout=StringIO(),
        )

        user = User.objects.get()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("admin"))

    def test_without_password(self):
        call_command(
            "createinitialsuperuser",
            "--username=admin",
            "--email=admin@example.com",
            "--no-input",
            stdout=StringIO(),
        )

        user = User.objects.get()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "admin@example.com")
        self.assertFalse(user.check_password("admin"))
