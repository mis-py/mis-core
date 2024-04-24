from abc import abstractmethod
from tortoise import fields
from tortoise.queryset import QuerySet
from tortoise.expressions import Q
from .permission import GrantedPermission, Permission


class PermissionsMixin:
    granted_permissions: fields.ReverseRelation['GrantedPermission']

    @abstractmethod
    async def get_relation_arg(self):
        raise TypeError(f"Can't use PermissionsMixin with type {self.__class__.__name__}")

    async def set_permissions(self, scopes_list: list):
        """
        Set list of permissions

        :param scopes_list: list of scopes to grant
        :return: True. Exactly, only True right now. Nothing else cant be returned :)
        """
        relation_arg = await self.get_relation_arg()

        await GrantedPermission.filter(**relation_arg).delete()  # clearing all previous permits
        to_create = [
            GrantedPermission(permission=permission, **relation_arg)  # creating new permits
            for permission in await Permission.filter(scope__in=scopes_list)
        ]
        await GrantedPermission.bulk_create(to_create)
        return True

    async def add_permission(self, scope: str):
        """
        Grant new permission for relation
        return: True if success added
        """
        relation_arg = await self.get_relation_arg()
        permission = await Permission.get_or_none(scope=scope)
        if not permission:
            return False
        await GrantedPermission.get_or_create(permission=permission, **relation_arg)
        return True

    async def remove_permission(self, scope: str):
        """
        Remove permission for relation
        return: True if success removed
        """
        relation_arg = await self.get_relation_arg()
        permission = await Permission.get_or_none(scope=scope)
        if not permission:
            return False
        await GrantedPermission.filter(permission=permission, **relation_arg).delete()
        return True

    @abstractmethod
    async def get_granted_permissions(self, scopes_list=False) -> QuerySet['GrantedPermission'] | list[str]:
        """
        Get list of granted permissions

        :param scopes_list: If True, then list of scopes will be returned.
        :return: list[GrantedPermission] | list[str]
        """
        raise TypeError(f"Can't use PermissionsMixin with type {self.__class__.__name__}")


class UserPermissionsMixin(PermissionsMixin):
    async def get_relation_arg(self):
        return {'user': self}

    async def get_granted_permissions(self, scopes_list=False) -> QuerySet['GrantedPermission'] | list[str]:
        query = GrantedPermission.filter(
            Q(user_id=self.id) | Q(user_id=self.id, team_id=self.team_id)
        )

        if scopes_list:
            query = query.select_related('permission')
            return [p.permission.scope for p in await query]
        return query


class TeamPermissionsMixin(PermissionsMixin):
    async def get_relation_arg(self):
        return {'team': self}

    async def get_granted_permissions(self, scopes_list=False) -> QuerySet['GrantedPermission'] | list[str]:
        query = GrantedPermission.filter(
            team_id=self.id
        )

        if scopes_list:
            query = query.select_related('permission')
            return [p.permission.scope for p in await query]
        return query


class GuardianMixin:
    """Mixin for use in models for access control"""

    @classmethod
    def get_all_subclasses(cls):
        subclasses = []
        for subclass in cls.__subclasses__():
            subclasses.append(subclass)
        return subclasses
