from abc import ABC, abstractmethod

from tortoise.queryset import QuerySet

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IRoutingKeyRepository(IRepository, ABC):

    @abstractmethod
    async def filter_by_user(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_unused(self, **kwargs):
        raise NotImplementedError


class RoutingKeyRepository(TortoiseORMRepository, IRoutingKeyRepository):
    async def filter_by_user(self, user_id: int) -> QuerySet:
        return self.model.filter(key_subscriptions__user_id=user_id)

    async def delete_unused(self, module_id: int, exist_keys: list[str]):
        return await self.model.filter(app_id=module_id) \
            .exclude(key__in=exist_keys).delete()
