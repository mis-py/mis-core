from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IScheduledJobRepository(IRepository, ABC):
    pass


class ScheduledJobRepository(TortoiseORMRepository, IScheduledJobRepository):
    pass
