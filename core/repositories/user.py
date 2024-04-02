from abc import ABC, abstractmethod

from core.db.models import User
from core.repositories.base.repository import IRepository, TortoiseORMRepository


class IUserRepository(IRepository, ABC):

    @abstractmethod
    async def find_by_ids(self, ids: list[int]):
        raise NotImplementedError


class UserRepository(TortoiseORMRepository, IUserRepository):
    async def find_by_ids(self, ids: list[int]) -> list[User]:
        return await self.model.filter(id__in=ids)
