from typing import Dict, List, NotRequired, TypedDict, Union


class ActingUser(TypedDict):
    identifier: int | str
    display_name: str


class MetadataDict(TypedDict):
    """
    Optimistic model for the metadata - unfortunately we can't add DB constraints.
    """

    event: str
    acting_user: ActingUser
    _cached_object_repr: NotRequired[str]


JSONPrimitive = str | int | float | bool | None
# Forward declaration for JSONValue to reference JSONObject
JSONValue = Union[JSONPrimitive, "JSONObject", List["JSONValue"]]
# JSONObject is a dictionary with string keys and JSONValue values
JSONObject = Dict[str, JSONValue]
