from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel

from .common import TrackerInstanceBaseModel

class ProxyDomainBaseModel(PydanticModel):
    id: int
    name: str
    date_added: datetime


class ProxyDomainModel(ProxyDomainBaseModel):
    tracker_instance: TrackerInstanceBaseModel
    is_invalid: bool
    is_ready: bool
    server_name: str


class ProxyDomainCreateModel(PydanticModel):
    domain_name: str
    tracker_instance_id: int
    server_name: str


class ProxyDomainCreateBulkModel(PydanticModel):
    domain_names: list[str]
    tracker_instance_id: int
    server_name: str


class ProxyDomainUpdateModel(PydanticModel):
    name: str
    tracker_instance_id: int
    server_name: str
    is_invalid: bool
    is_ready: bool


class ProxyDomainServerNameModels(PydanticModel):
    server_names: list[str]
