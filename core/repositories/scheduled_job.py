from abc import ABC, abstractmethod

from core.db.models import ScheduledJob
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IScheduledJobRepository(IRepository, ABC):
    @abstractmethod
    async def filter_by_module(self, **kwargs):
        raise NotImplementedError


class ScheduledJobRepository(TortoiseORMRepository, IScheduledJobRepository):
    model = ScheduledJob

    async def filter_by_module(self, module_name: str, prefetch_related: list = None) -> list:
        return await self.filter(app__name=module_name, prefetch_related=prefetch_related)
