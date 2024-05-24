from abc import ABC

from core.repositories.base.repository import TortoiseORMRepository, IRepository
from modules.dummy.db.models import DummyElementModel


class IDummyElementRepository(IRepository, ABC):
    pass


class DummyElementRepository(TortoiseORMRepository, IDummyElementRepository):
    model = DummyElementModel

    async def get_ids(self, **filters):
        return await self.model.filter(**filters).values_list("id", flat=True)
