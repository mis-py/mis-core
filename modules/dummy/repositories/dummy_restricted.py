from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository
from modules.dummy.db.models import DummyRestrictedModel


class IDummyRestrictedRepository(IRepository, ABC):
    pass


class DummyRestrictedRepository(TortoiseORMRepository, IDummyRestrictedRepository):
    model = DummyRestrictedModel
