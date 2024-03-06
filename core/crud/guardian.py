from core.db.guardian import (
    GuardianAccessGroup,
    GuardianPermission,
    GuardianContentType,
    GuardianGroupPermission,
    GuardianUserPermission,
)
from core.crud.base import CRUDBase
from core.db.models import User, Module


class CRUDGuardianAccessGroup(CRUDBase):

    async def create_group(self, name: str, module: Module) -> GuardianAccessGroup:
        return await self.model.create(name=name, module=module)

    async def update_group(self, group: GuardianAccessGroup, name: str) -> GuardianAccessGroup:
        group.name = name
        await group.save()
        return group

    async def add_users(self, group: GuardianAccessGroup, users: list[User]) -> None:
        await group.users.add(*users)

    async def set_group_users(self, group: GuardianAccessGroup, users: list[User]):
        """Clear old users and set new users"""
        await group.users.clear()
        await group.users.add(*users)


class CRUDGuardianPermission(CRUDBase):

    async def get_or_create(self, content_type: GuardianContentType, name: str, code_name: str):
        return await self.model.get_or_create(content_type=content_type, name=name, code_name=code_name)


class CRUDGuardianContentType(CRUDBase):
    async def join_module(self, queryset):
        return queryset.select_related('module')

    async def get_or_create(self, module: Module, model: str):
        return await self.model.get_or_create(module=module, model=model)


class CRUDGuardianUserPermission(CRUDBase):

    async def join_content_type_and_permission(self, queryset):
        return queryset.select_related('content_type__module', 'permission')

    async def add_permission(
            self,
            object_pk: str,
            content_type: GuardianContentType,
            permission: GuardianPermission,
            user: User,
    ):
        return await self.model.create(
            object_pk=object_pk,
            content_type=content_type,
            permission=permission,
            user=user,
        )


class CRUDGuardianGroupPermission(CRUDBase):
    async def join_content_type_and_permission(self, queryset):
        return queryset.select_related('content_type__module', 'permission')

    async def add_permission(
            self,
            object_pk: str,
            content_type: GuardianContentType,
            permission: GuardianPermission,
            group: GuardianAccessGroup,
    ):
        return await self.model.create(
            object_pk=object_pk,
            content_type=content_type,
            permission=permission,
            group=group,
        )



guardian_group = CRUDGuardianAccessGroup(GuardianAccessGroup)
guardian_permissions = CRUDGuardianPermission(GuardianPermission)
guardian_content_type = CRUDGuardianContentType(GuardianContentType)
guardian_user_perm = CRUDGuardianUserPermission(GuardianUserPermission)
guardian_group_perm = CRUDGuardianGroupPermission(GuardianGroupPermission)
