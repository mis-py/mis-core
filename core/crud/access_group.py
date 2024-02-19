from core.db.restricted import AccessGroup, RestrictedObject
from core.crud.base import CRUDBase
from core.db.models import User


class CRUDUserGroup(CRUDBase):
    async def create_with_users(self, name: str, users_ids: list[int], app_model=None) -> AccessGroup:
        """Create group and add users in group"""
        new_group = await self.model.create(name=name, app=app_model)

        if users_ids:
            users = await User.filter(id__in=users_ids)
            await new_group.users.add(*users)

        return new_group

    async def set_group_users(self, group: AccessGroup, users_ids: list[int]) -> list[User]:
        """Clear old users and set new users"""
        await group.users.clear()

        for user in await User.filter(id__in=users_ids):
            await user.groups.add(group)
        return await group.users

    async def set_allowed_objects(self, group: AccessGroup, objects_ids: list[int]) -> list[RestrictedObject]:
        """Clear old allowed_objects and set new objects"""
        await group.allowed_objects.clear()

        for obj in await RestrictedObject.filter(id__in=objects_ids):
            await obj.allowed_groups.add(group)
        return await group.allowed_objects

    async def get_users(self, group: AccessGroup) -> list[User]:
        """Get group users"""
        return await group.users

    async def get_allowed_objects(self, group: AccessGroup) -> list[RestrictedObject]:
        """Get group allowed objects"""
        return await group.allowed_objects


access_group = CRUDUserGroup(AccessGroup)
