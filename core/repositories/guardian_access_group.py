from abc import ABC, abstractmethod

from core.db.guardian import GuardianAccessGroup
from core.db.models import User
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGAccessGroupRepository(IRepository, ABC):

    @abstractmethod
    async def add_users(self, group, users):
        raise NotImplementedError

    @abstractmethod
    async def remove_users(self, group, users):
        raise NotImplementedError


class GAccessGroupRepository(TortoiseORMRepository, IGAccessGroupRepository):

    async def add_users(self, group: GuardianAccessGroup, users: list[User]):
        await group.users.add(*users)

    async def remove_users(self, group: GuardianAccessGroup, users: list[User]):
        await group.users.remove(*users)
