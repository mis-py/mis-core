from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel

from core.schemas.common import UserModelShort

from .proxy_domain import ProxyDomainBaseModel
from .replacement_group import ReplacementGroupModel


class ReplacementHistoryReadModel(PydanticModel):
    id: int
    from_domains: list[ProxyDomainBaseModel]
    to_domain: ProxyDomainBaseModel
    replaced_by: UserModelShort
    date_changed: datetime
    offers: list[str]
    lands: list[str]
    reason: str | None


class ReplacementGroupWithHistory(ReplacementGroupModel):
    replacement_history: list[ReplacementHistoryReadModel] = []
