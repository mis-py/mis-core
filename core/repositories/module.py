from abc import ABC, abstractmethod

from core.db.models import Module
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IModuleRepository(IRepository, ABC):
    @abstractmethod
    async def get_or_create_by_name(self, name: str):
        raise NotImplementedError


class ModuleRepository(TortoiseORMRepository, IModuleRepository):
    async def get_or_create_by_name(self, name: str) -> (Module, bool):
        return await self.model.get_or_create(name=name)
