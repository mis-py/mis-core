from core.db import UserGroup, User, RestrictedObject
from core.db.crud.base import CRUDBase


class CRUDUserGroup(CRUDBase):
    async def create_with_users(self, name: str, users_ids: list[int], app_model=None) -> UserGroup:
        """Create group and add users in group"""
        new_group = await self.model.create(name=name, app=app_model)

        if users_ids:
            users = await User.filter(id__in=users_ids)
            await new_group.users.add(*users)

        return new_group

    async def set_group_users(self, group: UserGroup, users_ids: list[int]):
        """Clear old users and set new users"""
        await group.users.clear()

        for user in await User.filter(id__in=users_ids):
            await user.groups.add(group)
        return await group.users

    async def set_allowed_objects(self, group: UserGroup, objects_ids: list[int]):
        """Clear old allowed_objects and set new objects"""
        await group.allowed_objects.clear()

        for obj in await RestrictedObject.filter(id__in=objects_ids):
            await obj.allowed_groups.add(group)
        return await group.allowed_objects

    async def get_users(self, group: UserGroup) -> list[User]:
        """Get group users"""
        return await group.users

    async def get_allowed_objects(self, group: UserGroup) -> list[User]:
        """Get group allowed objects"""
        return await group.allowed_objects


access_group = CRUDUserGroup(UserGroup)
