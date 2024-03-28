from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IScheduleJobRepository(IRepository, ABC):
    pass


class ScheduleJobRepository(TortoiseORMRepository, IScheduleJobRepository):
    pass
