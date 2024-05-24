from abc import ABC

from tortoise.query_utils import Prefetch

from core.repositories.base.repository import TortoiseORMRepository, IRepository
from modules.dummy.db.models import DummyGroupModel, DummyCategoryModel, DummyElementModel


class IDummyGroupRepository(IRepository, ABC):
    pass


class DummyGroupRepository(TortoiseORMRepository, IDummyGroupRepository):
    model = DummyGroupModel

    async def filter_queryable_with_elements(self, **filters):
        """Filter with custom Prefetch for filter and order nested relations"""
        return self.model.filter(**filters).prefetch_related(
            Prefetch(
                'categories',
                queryset=DummyCategoryModel.filter(name__contains='TEST').prefetch_related(
                    Prefetch(
                        'elements',
                        queryset=DummyElementModel.filter(name__contains='TEST').order_by('-created_at'),
                    )
                )
            )
        )
