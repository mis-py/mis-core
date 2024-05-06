from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel

from .dataclass import DomainStatus
from .models import ChangedDomain, Domain, BinomGeo


# TrackerInstanceModel = pydantic_model_creator(TrackerInstance, name='TrackerInstanceModel')
Tortoise.init_models(["modules.binom_companion.db.models"], 'binom_companion')

# ReplacementGroupModel = pydantic_model_creator(
#     ReplacementGroup,
#     name='ReplacementGroupModel',
#     # optional=('tracker_instance','replacement_history'),
#
#     exclude=(
#         'tracker_instance.proxy_domains',
#         'tracker_instance.replacement_history',
#         'replacement_history',
#         'tracker_instance.api_key'
#     )
# )

ChangedDomainModel = pydantic_model_creator(ChangedDomain, name='ChangedDomainModel')
DomainModel = pydantic_model_creator(Domain, name='DomainModel')
DomainUpdateModel = pydantic_model_creator(
    Domain, name='DomainUpdateModel', exclude_readonly=True, optional=('domain',))
GeoModel = pydantic_model_creator(BinomGeo, name='GeoModel')
GeoCreateModel = pydantic_model_creator(BinomGeo, name='GeoCreateModel', exclude_readonly=True,
                                        exclude=('task_check_statuses',))
GeoUpdateModel = pydantic_model_creator(BinomGeo, name='GeoUpdateModel', exclude_readonly=True,
                                        exclude=('task_check_statuses',), optional=('name',))


class GeoSimpleModel(PydanticModel):
    id: int
    name: str

    class Config:
        orig_model = BinomGeo


class GeoOutModel(PydanticModel):
    id: int
    user_id: Optional[int]
    name: str
    is_check: bool
    diff_percent: int
    domain_change_cooldown: int
    last_period_duration: int
    previous_period_duration: int
    time_since_last_lead: int
    task_check_statuses: Optional[dict]

    class Config:
        orig_model = BinomGeo


class DomainCreateModel(BaseModel):
    domain: str
    status: DomainStatus
    allowed_geo: list[int]
    ip: Optional[str]
    registrator: Optional[str]
    vds_service: Optional[str]
    additional_info: Optional[str]


class DomainListCreateModel(BaseModel):
    domain: list[str]
    status: DomainStatus
    allowed_geo: list[int]


class DomainOutModel(PydanticModel):
    id: int
    domain: str
    ip: Optional[str]
    registrator: Optional[str]
    vds_service: Optional[str]
    additional_info: Optional[str]
    status: DomainStatus
    current_geo: Optional[GeoOutModel]
    allowed_geo: list[GeoSimpleModel]
    banned_geo: list[GeoSimpleModel]
    created: datetime
    updated: datetime

    class Config:
        orig_model = Domain
