from abc import ABC, abstractmethod

from core.db.models import User
from core.repositories.base.repository import IRepository, TortoiseORMRepository


class IUserRepository(IRepository, ABC):

    @abstractmethod
    async def find_by_ids(self, ids: list[int]):
        raise NotImplementedError

    @abstractmethod
    async def filter_by_subscription(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update_by_kwargs(self, user_id: int, **kwargs):
        raise NotImplementedError

class UserRepository(TortoiseORMRepository, IUserRepository):
    model = User

    async def find_by_ids(self, ids: list[int]) -> list[User]:
        return await self.model.filter(id__in=ids)

    async def filter_by_subscription(self, routing_key: str, query=None):
        query = query if query else self.model.filter()
        return await query.filter(
            subscriptions__isnull=False,
            subscriptions__routing_key__key=routing_key,
        ).distinct()

    async def update_by_kwargs(self, user_id: int, **kwargs):
        return await self.update(id=user_id, data=kwargs)
