from tortoise.contrib.pydantic import PydanticModel

from .common import ReplacementHistoryBaseModel, TrackerInstanceBaseModel


class ReplacementGroupBaseModel(PydanticModel):
    id: int
    name: str
    description: str


class ReplacementGroupShortModel(ReplacementGroupBaseModel):
    tracker_instance: TrackerInstanceBaseModel


class ReplacementGroupModel(ReplacementGroupShortModel):
    id: int
    name: str
    description: str

    offer_group_id: int
    offer_geo: str
    offer_name_regexp_pattern: str

    land_group_id: int
    land_language: str
    land_name_regexp_pattern: str

    is_active: bool


class ReplacementGroupCreateModel(PydanticModel):
    name: str
    description: str

    offer_group_id: int
    offer_geo: str
    offer_name_regexp_pattern: str

    land_group_id: int
    land_language: str
    land_name_regexp_pattern: str

    tracker_instance_id: int

    is_active: bool


class ReplacementGroupUpdateModel(PydanticModel):
    name: str
    description: str

    offer_group_id: int
    offer_geo: str
    offer_name_regexp_pattern: str

    land_group_id: int
    land_language: str
    land_name_regexp_pattern: str

    tracker_instance_id: int

    is_active: bool


class ReplacementGroupChangeProxyIds(PydanticModel):
    replacement_group_ids: list[int]
