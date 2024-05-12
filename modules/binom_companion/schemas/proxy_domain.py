from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel


class ProxyDomainBaseModel(PydanticModel):
    id: int
    name: str
    date_added: datetime


class ProxyDomainModel(ProxyDomainBaseModel):
    tracker_instance_id: int


class ProxyDomainCreateModel(PydanticModel):
    name: str
    tracker_instance_id: int


class ProxyDomainUpdateModel(PydanticModel):
    name: str
    tracker_instance_id: int
