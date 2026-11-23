# Taken from github.com/open-zaak/open-zaak project
# Copyright (C) 2020 Dimpact
import os
from typing import ClassVar

from django.conf import settings
from django.contrib.auth.management.commands.createsuperuser import (
    Command as BaseCommand,
)
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
from django.core.management.base import CommandParser
from django.urls import reverse
from django.utils.crypto import get_random_string

from typing_extensions import TypeIs


class Command(BaseCommand):
    help = "Set up an initial superuser account if it doesn't exist yet"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)

        parser.add_argument(
            "--password",
            help="Set the password when the superuser is initially created.",
        )
        parser.add_argument(
            "--generate-password",
            action="store_true",
            help=(
                "Generate and e-mail the password. The --password option and "
                "environment variable overrule this flag."
            ),
        )
        parser.add_argument(
            "--email-password-reset",
            action="store_true",
            help="Send a password reset e-mail after user creation.",
        )
        parser.add_argument(
            "--domain",
            help="Domain the app is deployed on. Falls back to settings.ALLOWED_HOSTS[0].",
        )

    def handle(
        self,
        *,
        password: str | None,
        generate_password: bool,
        email_password_reset: bool,
        domain: str | None,
        **options: object,
    ) -> None:
        if not is_custom_user_class(self.UserModel):
            raise TypeError(f"{self.UserModel} does not satisfy CustomUserProtocol")

        username = options[self.UserModel.USERNAME_FIELD]
        database = options["database"]
        assert isinstance(database, str)

        qs = self.UserModel._default_manager.db_manager(database).filter(
            **{self.UserModel.USERNAME_FIELD: username}
        )
        if qs.exists():
            self.stdout.write(
                self.style.WARNING("Superuser account already exists, exiting")
            )
            return

        password = password or os.environ.get("OPENPRODUCT_SUPERUSER_PASSWORD")

        if password or generate_password:
            options["interactive"] = False

        # perform user creation from core Django
        super().handle(**options)

        user = qs.get()

        if not password and generate_password:
            password = get_random_string(20)

        if password:
            self.stdout.write("Setting user password...")
            user.set_password(password)
            user.save()

        if email_password_reset:
            password_reset_path = reverse("admin_password_reset")
            default_host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else ""
            assert isinstance(default_host, str)
            if default_host == "*":
                default_host = ""

            domain = domain or default_host

            pw_reset_link = (
                f"https://{domain}{password_reset_path}" if domain else "unknown url"
            )
            subject = (
                f"Your admin user for {settings.PROJECT_NAME} "
                f"({domain or 'unknown url'})"
            )
            send_mail(
                subject,
                (
                    f"Credentials for project: {settings.PROJECT_NAME}\n\n"
                    f"Username: {username}\nPassword reset link: {pw_reset_link}"
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )


class CustomUserProtocol(AbstractBaseUser):
    USERNAME_FIELD: ClassVar[str]
    email: str

    class Meta(AbstractBaseUser.Meta):
        # prevent needing an app_label for this Protocol hack.
        abstract = True


def is_custom_user_class(
    cls: type[AbstractBaseUser],
) -> TypeIs[type[CustomUserProtocol]]:
    "Validate the User Model meets our protocol shape"
    return all(hasattr(cls, attr) for attr in CustomUserProtocol.__annotations__)
