from abc import ABC, abstractmethod

from core.db.models import Variable
from core.repositories.base.repository import IRepository, TortoiseORMRepository


class IVariableRepository(IRepository, ABC):
    @abstractmethod
    async def get_or_create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_unused(self, **kwargs):
        raise NotImplementedError


class VariableRepository(TortoiseORMRepository, IVariableRepository):
    model = Variable

    async def get_or_create(
            self,
            module_id: int,
            key: str,
            default_value: str | int | float,
            is_global: bool,
            type: str
    ):
        return await self.model.get_or_create(
            app_id=module_id,
            key=key,
            is_global=is_global,
            type=type,
            defaults={'default_value': default_value},
        )

    async def delete_unused(self, module_id: int, exist_keys: list[str]):
        return await self.model.filter(app_id=module_id).exclude(key__in=exist_keys).delete()
