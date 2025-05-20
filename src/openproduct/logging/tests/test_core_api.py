from django.test import TestCase

from openproduct.accounts.tests.factories import UserFactory

from ..constants import Events
from ..logevent import _audit_event


class LogEventTests(TestCase):
    def test_raises_if_no_user_information_provided(self):
        content_object = UserFactory.create()

        with (
            self.subTest("no django_user, no user_id, no user_display"),
            self.assertRaises(ValueError),
        ):
            _audit_event(
                content_object=content_object,
                event=Events.read,
                django_user=None,
                user_id="",
                user_display="",
            )

        with (
            self.subTest("no django_user, with user_id, no user_display"),
            self.assertRaises(ValueError),
        ):
            _audit_event(
                content_object=content_object,
                event=Events.read,
                django_user=None,
                user_id="foo",
                user_display="",
            )

        with (
            self.subTest("no django_user, no user_id, with user_display"),
            self.assertRaises(ValueError),
        ):
            _audit_event(
                content_object=content_object,
                event=Events.read,
                django_user=None,
                user_id="",
                user_display="bar",
            )
