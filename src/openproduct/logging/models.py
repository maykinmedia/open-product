from typing import Literal

from django.utils.translation import gettext_lazy as _

from timeline_logger.models import TimelineLog

from openproduct.accounts.models import User

from .constants import Events
from .typing import ActingUser, MetadataDict


class TimelineLogProxy(TimelineLog):
    """
    Proxy the Python API of the package model.

    django-timeline-logger is agnostic, so we provide a convenience wrapper via this
    proxy model.
    """

    content_type_id: int | None

    extra_data: MetadataDict | None

    class Meta:  # pyright: ignore
        proxy = True
        verbose_name = _("(audit) log entry")
        verbose_name_plural = _("(audit) log entries")

    def save(self, *args, **kwargs):
        # there's a setting for this, but then makemigrations produces a new migration
        # in the third party package which is less than ideal...
        if self.template == "timeline_logger/default.txt":
            self.template = "logging/message.txt"

        if self.extra_data is None:
            raise ValueError("'extra_data' may not be empty.")
        if not isinstance(self.extra_data, dict):
            raise TypeError("'extra_data' must be a JSON object (python dict).")

        # ensure that we always track the event
        self._validate_event()
        # ensure that we always track the acting user
        self._validate_user_details()
        self._cache_object_repr()

        super().save(*args, **kwargs)

    def _cache_object_repr(self) -> None:
        # cache the object representation so we can avoid querying the content_object
        # in the admin list page, which does wonders for performance
        assert self.extra_data is not None
        if not self.object_id or not self.content_type_id:
            return
        self.extra_data["_cached_object_repr"] = str(self.content_object)

    def _validate_event(self):
        assert self.extra_data is not None
        try:
            Events(self.extra_data["event"])
        except (ValueError, KeyError) as enum_error:
            raise ValueError(
                "The extra data must contain an 'event' key from the "
                "'woo_publications.logging.constants.Events' enum."
            ) from enum_error

    def _validate_user_details(self):
        """
        Validate that the extra metadata contains snapshot data of the acting user.

        Note that we track a FK to the django user model too, but we also store audit
        log events of users that don't exist in our local database. Additionally, if
        a user is deleted, we want to retain the audit logs of them.
        """
        assert self.extra_data is not None
        try:
            user_details = self.extra_data["acting_user"]
        except KeyError as err:
            raise ValueError(
                "Audit logs must contain the 'acting_user' key in the metadata."
            ) from err

        try:
            user_details["identifier"]
            user_details["display_name"]
        except (KeyError, TypeError) as err:
            raise ValueError(
                "The user details in audit logs must contain the 'identifier' and "
                "'display_name' keys."
            ) from err

    def get_related_object_repr(self) -> str:
        if not self.object_id or not self.content_type_id:
            return ""
        if (
            self.extra_data is None
            or (obj_repr := self.extra_data.get("_cached_object_repr")) is None
        ):
            return str(self.content_object)
        return obj_repr

    @property
    def event(self) -> Events | Literal["unknown"]:
        """
        Extract the semantic event from the metadata.

        It's possible log records exist that have an 'event' value that was once defined
        in code, but no longer is - in that case, the literal string "unknown" is
        returned.
        """
        match self.extra_data:
            case {"event": str() as _event}:
                try:
                    return Events(_event)
                except ValueError:
                    return "unknown"
            case _:
                return "unknown"

    @property
    def acting_user(self) -> tuple[ActingUser, User | None]:
        """
        Get information of the acting user.

        Returns a tuple that always contains the recorded acting user metadata as first
        element. The second element is the Django user instance if it is known,
        otherwise ``None``.
        """
        acting_user: ActingUser = {"identifier": "unknown", "display_name": "unknown"}
        match self.extra_data:
            case {"acting_user": _acting_user} if isinstance(_acting_user, dict):
                acting_user = _acting_user
                acting_user.setdefault("identifier", "unknown")
                acting_user.setdefault("display_name", "unknown")
            case _:
                pass
        return (acting_user, self.user)
