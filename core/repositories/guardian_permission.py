from abc import ABC, abstractmethod

from core.db.guardian import GuardianPermission
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IGPermissionRepository(IRepository, ABC):
    @abstractmethod
    async def group_perms_list(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def multi_group_perms_list(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def users_perms_list(self, **kwargs):
        raise NotImplementedError


class GPermissionRepository(TortoiseORMRepository, IGPermissionRepository):
    model = GuardianPermission

    async def group_perms_list(self, model: str, group_id: int, object_pk: str):
        return await self.model.filter(
            content_type__model=model,
            group_permissions__group_id=group_id,
            group_permissions__object_pk=object_pk,
        ).values_list("code_name", flat=True)

    async def multi_group_perms_list(self, model: str, groups_ids: list[int], object_pk: str):
        return await self.model.filter(
            content_type__model=model,
            group_permissions__group_id__in=groups_ids,
            group_permissions__object_pk=object_pk,
        ).distinct().values_list("code_name", flat=True)

    async def users_perms_list(self, model: str, user_id: int, object_pk: str):
        return await self.model.filter(
            user_permissions__user_id=user_id,
            content_type__model=model,
            user_permissions__object_pk=object_pk,
        ).distinct().values_list("code_name", flat=True)
