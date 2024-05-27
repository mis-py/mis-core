from .common import ReplacementHistoryBaseModel
from .proxy_domain import ProxyDomainBaseModel
from .replacement_group import ReplacementGroupShortModel


class ReplacementHistoryModel(ReplacementHistoryBaseModel):
    from_domains: list[ProxyDomainBaseModel]
    to_domain: ProxyDomainBaseModel
    replacement_group: ReplacementGroupShortModel
    offers: list[str]
    lands: list[str]

