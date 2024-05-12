from tortoise.contrib.pydantic import PydanticModel
from .replacement_group import ReplacementGroupBaseModel


class TrackerInstanceBaseModel(PydanticModel):
    id: int
    name: str
    description: str


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


class TrackerInstanceUpdateModel(PydanticModel):
    name: str
    description: str
    api_key: str
    base_url: str
    get_route: str
    edit_route: str
