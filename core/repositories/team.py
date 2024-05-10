from abc import ABC

from core.db.models import Team
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class ITeamRepository(IRepository, ABC):
    pass


class TeamRepository(TortoiseORMRepository, ITeamRepository):
    model = Team
