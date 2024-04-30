from abc import ABC, abstractmethod

from core.repositories.base.repository import IRepository, TortoiseORMRepository


class IVariableRepository(IRepository, ABC):
    @abstractmethod
    async def get_or_create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_unused(self, **kwargs):
        raise NotImplementedError


class VariableRepository(TortoiseORMRepository, IVariableRepository):
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
            default_value=default_value,
            is_global=is_global,
            type=type,
        )

    async def delete_unused(self, module_id: int, exist_keys: list[str]):
        return await self.model.filter(app_id=module_id).exclude(key__in=exist_keys).delete()
