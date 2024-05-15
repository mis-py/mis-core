from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel

from core.schemas.common import UserModelShort

from .proxy_domain import ProxyDomainBaseModel
from .replacement_group import ReplacementGroupShortModel


class ReplacementHistoryBaseModel(PydanticModel):
    id: int
    from_domains: list[ProxyDomainBaseModel]
    to_domain: ProxyDomainBaseModel
    replacement_group: ReplacementGroupShortModel
    replaced_by: UserModelShort
    date_changed: datetime


class ReplacementHistoryModel(ReplacementHistoryBaseModel):
    offers: str
    lands: str
    reason: str
