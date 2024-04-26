from abc import ABC, abstractmethod

from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGGroupPermissionRepository(IRepository, ABC):
    @abstractmethod
    async def get_or_create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_objects_pks(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_objects_pks_by_multi_groups(self, **kwargs):
        raise NotImplementedError


class GGroupPermissionRepository(TortoiseORMRepository, IGGroupPermissionRepository):
    async def get_or_create(self, group_id: int, permission_id: int, content_type_id: int, object_pk):
        return await self.model.get_or_create(
            group_id=group_id,
            permission_id=permission_id,
            content_type_id=content_type_id,
            object_pk=object_pk,
        )


    async def get_objects_pks(self, group_id: int, model: str, perm: str):
        return await self.model.filter(
            group_id=group_id,
            permission__code_name=perm,
            content_type__model=model,
        ).values_list("objects_pk", flat=True)

    async def get_objects_pks_by_multi_groups(self, groups_ids: list[int], model: str, perm: str):
        return await self.model.filter(
            group__id__in=groups_ids,
            permission__code_name=perm,
            content_type__model=model,
        ).values_list("objects_pk", flat=True)
