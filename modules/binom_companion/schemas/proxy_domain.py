from datetime import datetime
from typing import Optional

from tortoise.contrib.pydantic import PydanticModel

from .common import TrackerInstanceBaseModel

class ProxyDomainBaseModel(PydanticModel):
    id: int
    name: str
    date_added: datetime


class ProxyDomainModel(ProxyDomainBaseModel):
    tracker_instances: list[TrackerInstanceBaseModel]
    is_invalid: bool
    is_ready: bool
    server_name: str


class ProxyDomainCreateModel(PydanticModel):
    name: str
    tracker_instance_ids: list[int]
    server_name: str


class ProxyDomainCreateBulkModel(PydanticModel):
    domain_names: list[str]
    tracker_instance_ids: list[int]
    server_name: str


class ProxyDomainUpdateModel(PydanticModel):
    name: str
    tracker_instance_ids: list[int]
    server_name: str
    is_invalid: bool
    is_ready: bool


class ProxyDomainUpdatePartiallyModel(PydanticModel):
    id: int
    name: Optional[str] = None
    tracker_instance_ids: Optional[list[int]] = None
    server_name: Optional[str] = None
    is_invalid: Optional[bool] = None
    is_ready: Optional[bool] = None


class ProxyDomainBulkUpdateModel(PydanticModel):
    proxy_domains: list[ProxyDomainUpdatePartiallyModel]


class ProxyDomainServerNameModels(PydanticModel):
    server_names: list[str]
