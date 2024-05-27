from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository
from modules.dummy.db.models import DummyModel


class IDummyRepository(IRepository, ABC):
    pass


class DummyRepository(TortoiseORMRepository, IDummyRepository):
    model = DummyModel
