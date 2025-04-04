from .constants import Events
from .models import TimelineLogProxy
from .typing import ActingUser

__all__ = [
    "ModelOwnerMixin",
]


class ModelOwnerMixin:
    """
    Adds get_owner func to retrieve the TimeLineLog initial create object to retrieve the owner of the model.
    """

    def get_owner(self) -> ActingUser | None:
        """
        Extract the owner from the audit trails.
        """
        qs = TimelineLogProxy.objects.for_object(  # pyright: ignore[reportAttributeAccessIssue]
            self
        )
        try:
            log = qs.get(extra_data__event=Events.create)
        except TimelineLogProxy.DoesNotExist:
            return None
        assert isinstance(log, TimelineLogProxy)
        return log.acting_user[0]
