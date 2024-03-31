from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class ITeamRepository(IRepository, ABC):
    pass


class TeamRepository(TortoiseORMRepository, ITeamRepository):
    pass
