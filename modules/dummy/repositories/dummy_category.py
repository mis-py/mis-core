from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository
from modules.dummy.db.models import DummyCategoryModel


class IDummyCategoryRepository(IRepository, ABC):
    pass


class DummyCategoryRepository(TortoiseORMRepository, IDummyCategoryRepository):
    model = DummyCategoryModel
