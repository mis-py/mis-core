from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel
from .proxy_domain import ProxyDomainBaseModel
from .replacement_group import ReplacementGroupShortModel


class ReplacementHistoryBaseModel(PydanticModel):
    from_domains: list[ProxyDomainBaseModel]
    to_domain: ProxyDomainBaseModel
    replacement_group: ReplacementGroupShortModel
    replaced_by: int

    date_changed: datetime


class ReplacementHistoryModel(ReplacementHistoryBaseModel):
    offers: str
    lands: str
