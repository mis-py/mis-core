from tortoise.contrib.pydantic import PydanticModel
from .replacement_group import ReplacementGroupBaseModel
from .common import TrackerInstanceBaseModel
from ..db.models import TrackerType


class TrackerInstanceShortModel(TrackerInstanceBaseModel):
    replacement_groups: list[ReplacementGroupBaseModel]


class TrackerInstanceModel(TrackerInstanceShortModel):
    # api_key: str
    base_url: str
    get_route: str
    edit_route: str


class TrackerInstanceCreateModel(PydanticModel):
    name: str
    description: str
    api_key: str
    base_url: str
    get_route: str
    edit_route: str
    tracker_type: TrackerType


class TrackerInstanceUpdateModel(PydanticModel):
    name: str
    description: str
    api_key: str
    base_url: str
    get_route: str
    edit_route: str
