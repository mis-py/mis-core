from typing import Any
from datetime import datetime

from tortoise.contrib.pydantic import PydanticModel

from core.schemas.common import UserModelShort
from modules.binom_companion.schemas.proxy_domain import ProxyDomainBaseModel
from modules.binom_companion.schemas.replacement_group import ReplacementGroupModel


class ReplacementHistoryReadModel(PydanticModel):
    id: int
    from_domains: list[ProxyDomainBaseModel]
    to_domain: ProxyDomainBaseModel
    replaced_by: UserModelShort
    date_changed: datetime
    offers: str
    lands: str
    reason: str


class ReplacementGroupWithHistory(ReplacementGroupModel):
    replacement_history: list[ReplacementHistoryReadModel] = []
