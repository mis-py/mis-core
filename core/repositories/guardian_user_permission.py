from abc import ABC, abstractmethod

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGUserPermissionRepository(IRepository, ABC):
    @abstractmethod
    async def get_or_create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_objects_pks(self, **kwargs):
        raise NotImplementedError


class GUserPermissionRepository(TortoiseORMRepository, IGUserPermissionRepository):
    async def get_or_create(self, user_id: int, permission_id: int, content_type_id: int, object_pk):
        return await self.model.get_or_create(
            user_id=user_id,
            permission_id=permission_id,
            content_type_id=content_type_id,
            object_pk=object_pk,
        )

    async def get_objects_pks(self, user_id: int, model: str, perm: str):
        return await self.model.filter(
            user_id=user_id,
            permission__code_name=perm,
            content_type__model=model,
        ).values_list("objects_pk", flat=True)
