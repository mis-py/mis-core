from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel

from core.schemas.user import UserShortModel

from .proxy_domain import ProxyDomainBaseModel
from .replacement_group import ReplacementGroupShortModel


class ReplacementHistoryBaseModel(PydanticModel):
    id: int
    from_domains: list[ProxyDomainBaseModel]
    to_domain: ProxyDomainBaseModel
    replacement_group: ReplacementGroupShortModel
    replaced_by: UserShortModel
    date_changed: datetime


class ReplacementHistoryModel(ReplacementHistoryBaseModel):
    offers: str
    lands: str
