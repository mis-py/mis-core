from abc import ABC, abstractmethod

from tortoise.queryset import QuerySet

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IRoutingKeyRepository(IRepository, ABC):

    @abstractmethod
    async def filter_by_user(self, **kwargs):
        raise NotImplementedError


class RoutingKeyRepository(TortoiseORMRepository, IRoutingKeyRepository):
    async def filter_by_user(self, user_id: int) -> QuerySet:
        return self.model.filter(key_subscriptions__user_id=user_id)
