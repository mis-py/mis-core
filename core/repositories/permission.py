from abc import ABC, abstractmethod

from core.db.permission import Permission
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IPermissionRepository(IRepository, ABC):
    @abstractmethod
    async def delete_unused(self, **kwargs):
        raise NotImplementedError


class PermissionRepository(TortoiseORMRepository, IPermissionRepository):
    model = Permission

    async def delete_unused(self, module_id: int, exist_ids: list[int]):
        return await self.model.filter(app_id=module_id).exclude(id__in=exist_ids).delete()
