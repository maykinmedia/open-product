from django.test import TestCase

from timeline_logger.models import TimelineLog

from openproduct.accounts.tests.factories import UserFactory

from ..constants import Events
from ..models import TimelineLogProxy


class ProxyModelTests(TestCase):

    def test_extra_metadata_required(self):
        with (
            self.subTest("extra_data=null not allowed"),
            self.assertRaisesMessage(ValueError, "'extra_data' may not be empty."),
        ):
            TimelineLogProxy.objects.create(extra_data=None)

        with (
            self.subTest("extra_data top level must be dict"),
            self.assertRaisesMessage(TypeError, "'extra_data' must be a JSON object"),
        ):
            TimelineLogProxy.objects.create(extra_data=["foo"])

    def test_event_must_be_specified_and_valid(self):
        extra_data_base = {
            "acting_user": {"identifier": 123, "display_name": "Herbert"},
        }

        for invalid in (
            {},
            {"event": "afterPartyOnceTheProjectIsDone"},
        ):
            with (
                self.subTest("unknown event is blocked"),
                self.assertRaisesMessage(
                    ValueError, "The extra data must contain an 'event' key from"
                ),
            ):
                TimelineLogProxy.objects.create(
                    extra_data={**extra_data_base, **invalid},
                )

        for value, _ in Events.choices:
            with self.subTest("known events are valid", event=value):
                extra_data = {
                    **extra_data_base,
                    "event": value,
                }

                result = TimelineLogProxy.objects.create(extra_data=extra_data)

                self.assertIsNotNone(result.pk)

    def test_event_extraction(self):
        with self.subTest("log record complying with the validation rules"):
            record = TimelineLogProxy.objects.create(
                extra_data={
                    "event": Events.read,
                    "acting_user": {"identifier": 123, "display_name": "Herbert"},
                }
            )

            self.assertIs(record.event, Events.read)

        with self.subTest("log records with absent key"):
            # we can't guarantee that corrupt data will never enter the database due
            # to external factors or mistakes made in the future by developers. our
            # code needs to be robust for those situations
            _broken_record_1 = TimelineLog.objects.create(extra_data=None)
            _broken_record_2 = TimelineLog.objects.create(extra_data={})
            _broken_record_3 = TimelineLog.objects.create(extra_data=[])

            broken_record_1 = TimelineLogProxy.objects.get(pk=_broken_record_1.pk)
            self.assertEqual(broken_record_1.event, "unknown")

            broken_record_2 = TimelineLogProxy.objects.get(pk=_broken_record_2.pk)
            self.assertEqual(broken_record_2.event, "unknown")

            broken_record_3 = TimelineLogProxy.objects.get(pk=_broken_record_3.pk)
            self.assertEqual(broken_record_3.event, "unknown")

        with self.subTest("log record with unexpected event value"):
            _broken_record_4 = TimelineLog.objects.create(
                extra_data={
                    "event": "wildAfterPartyFollowingTheRelease",
                }
            )

            broken_record_4 = TimelineLogProxy.objects.get(pk=_broken_record_4.pk)
            self.assertEqual(broken_record_4.event, "unknown")

    def test_acting_user_must_be_specified_and_valid(self):
        extra_data_base = {"event": Events.read}

        with (
            self.subTest("missing acting_user key"),
            self.assertRaisesMessage(
                ValueError,
                "Audit logs must contain the 'acting_user' key in the metadata.",
            ),
        ):
            TimelineLogProxy.objects.create(extra_data={"event": Events.read})

        invalid_user_samples = (
            {},
            [],
            None,
            123,
            {"foo": "bar"},
            {"identifier": "123"},
            {"identifier": 123},
            {"display_name": "Annie"},
        )
        for invalid in invalid_user_samples:
            with (
                self.subTest("invalid user details are blocked", user_data=invalid),
                self.assertRaisesMessage(
                    ValueError,
                    "The user details in audit logs must contain the 'identifier' "
                    "and 'display_name' keys.",
                ),
            ):
                TimelineLogProxy.objects.create(
                    extra_data={**extra_data_base, "acting_user": invalid},
                )

        valid_user_samples = (
            {"identifier": "123", "display_name": "Annie"},
            {"identifier": 123, "display_name": "Annie"},
        )
        for valid in valid_user_samples:
            with self.subTest("valid data is accepted", user_data=valid):
                extra_data = {**extra_data_base, "acting_user": valid}

                result = TimelineLogProxy.objects.create(extra_data=extra_data)

                self.assertIsNotNone(result.pk)

    def test_acting_user_extraction(self):
        # we can't guarantee that corrupt data will never enter the database due
        # to external factors or mistakes made in the future by developers. our
        # code needs to be robust for those situations

        with self.subTest(
            "log record complying with the validation rules, no django user"
        ):
            record = TimelineLogProxy.objects.create(
                extra_data={
                    "event": Events.read,
                    "acting_user": {"identifier": 123, "display_name": "Herbert"},
                }
            )

            acting_user, django_user = record.acting_user

            self.assertIsNone(django_user)
            self.assertEqual(
                acting_user,
                {
                    "identifier": 123,
                    "display_name": "Herbert",
                },
            )

        with self.subTest(
            "log record complying with the validation rules, with django user"
        ):
            _django_user = UserFactory.create()
            record = TimelineLogProxy.objects.create(
                user=_django_user,
                extra_data={
                    "event": Events.read,
                    "acting_user": {"identifier": 123, "display_name": "Herbert"},
                },
            )

            acting_user, django_user = record.acting_user

            self.assertIsNotNone(django_user)
            self.assertEqual(django_user, _django_user)
            self.assertEqual(
                acting_user,
                {
                    "identifier": 123,
                    "display_name": "Herbert",
                },
            )

        with self.subTest("log records with absent key"):
            _broken_record_1 = TimelineLog.objects.create(extra_data=None)
            _broken_record_2 = TimelineLog.objects.create(extra_data={})
            _broken_record_3 = TimelineLog.objects.create(extra_data=[])

            broken_record_1 = TimelineLogProxy.objects.get(pk=_broken_record_1.pk)
            _acting_user_1 = broken_record_1.acting_user[0]
            self.assertEqual(
                _acting_user_1,
                {"identifier": "unknown", "display_name": "unknown"},
            )

            broken_record_2 = TimelineLogProxy.objects.get(pk=_broken_record_2.pk)
            _acting_user_2 = broken_record_2.acting_user[0]
            self.assertEqual(
                _acting_user_2,
                {"identifier": "unknown", "display_name": "unknown"},
            )

            broken_record_3 = TimelineLogProxy.objects.get(pk=_broken_record_3.pk)
            _acting_user_3 = broken_record_3.acting_user[0]
            self.assertEqual(
                _acting_user_3,
                {"identifier": "unknown", "display_name": "unknown"},
            )

        with self.subTest("log records with incomplete data"):
            _broken_record_4 = TimelineLog.objects.create(
                extra_data={"acting_user": {"identifier": 123}}
            )
            _broken_record_5 = TimelineLog.objects.create(
                extra_data={"acting_user": {"display_name": "Margareth"}}
            )

            broken_record_4 = TimelineLogProxy.objects.get(pk=_broken_record_4.pk)
            _acting_user_4 = broken_record_4.acting_user[0]
            self.assertEqual(
                _acting_user_4,
                {"identifier": 123, "display_name": "unknown"},
            )

            broken_record_5 = TimelineLogProxy.objects.get(pk=_broken_record_5.pk)
            _acting_user_5 = broken_record_5.acting_user[0]
            self.assertEqual(
                _acting_user_5,
                {"identifier": "unknown", "display_name": "Margareth"},
            )
