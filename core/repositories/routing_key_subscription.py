from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IRoutingKeySubscriptionRepository(IRepository, ABC):
    pass


class RoutingKeySubscriptionRepository(TortoiseORMRepository, IRoutingKeySubscriptionRepository):
    pass
