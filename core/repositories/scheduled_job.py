from abc import ABC, abstractmethod

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IScheduledJobRepository(IRepository, ABC):
    @abstractmethod
    async def filter_by_module(self, **kwargs):
        raise NotImplementedError


class ScheduledJobRepository(TortoiseORMRepository, IScheduledJobRepository):
    async def filter_by_module(self, module_name: str, prefetch_related: list = None) -> list:
        return await self.filter(app__name=module_name, prefetch_related=prefetch_related)
