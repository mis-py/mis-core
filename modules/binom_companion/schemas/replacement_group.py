from tortoise.contrib.pydantic import PydanticModel


class ReplacementGroupBaseModel(PydanticModel):
    id: int
    name: str
    description: str


class ReplacementGroupShortModel(ReplacementGroupBaseModel):
    tracker_instance_id: int
    # tracker_instance: TrackerInstanceBaseModel


class ReplacementGroupModel(ReplacementGroupShortModel):
    id: int
    name: str
    description: str

    aff_networks_ids: list[int]

    offer_group_id: int
    offer_geo: str
    offer_name_regexp_pattern: str

    land_group_id: int
    land_language: str
    land_name_regexp_pattern: str

    is_active: bool

    lead_record_ttl: int
    proxy_fail_check_coefficient: float
    lead_decrease_check_coefficient: float
    minimum_required_coefficient: float


class ReplacementGroupCreateModel(PydanticModel):
    name: str
    description: str
    aff_networks_ids: list[int]

    offer_group_id: int
    offer_geo: str
    offer_name_regexp_pattern: str

    land_group_id: int
    land_language: str
    land_name_regexp_pattern: str

    lead_record_ttl: int
    proxy_fail_check_coefficient: float
    lead_decrease_check_coefficient: float
    minimum_required_coefficient: float

    tracker_instance_id: int
