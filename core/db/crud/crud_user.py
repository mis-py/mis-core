from tortoise.queryset import QuerySet

from core.db import User, UserGroup
from core.db.crud.base import CRUDBase, CreateSchemaType, UpdateSchemaType


class CRUDUser(CRUDBase):
    async def create(self, obj_in: CreateSchemaType) -> User:
        """Create user with password"""
        new_user = User(
            username=obj_in.username,
            team_id=obj_in.team_id,
            position=obj_in.position,
        )
        new_user.set_password(obj_in.password)
        await new_user.save()
        return new_user

    async def update(self, db_obj: User, obj_in: UpdateSchemaType) -> User:
        """Update user with new password"""

        user = db_obj

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if "new_password" in update_data:
            new_password = update_data.pop("new_password")
            user.set_password(new_password)

        await user.update_from_dict(update_data).save()
        return user

    async def set_user_groups(self, user: User, groups_ids: list[int]):
        """Clear old user groups and set new"""
        await user.groups.clear()
        for group in await UserGroup.filter(id__in=groups_ids):
            await user.groups.add(group)
        return user

    async def query_get_by_subscription(self, routing_key: str, query: QuerySet = None):
        """Get or modify users queryset who subscribed on routing_key"""
        query = query if query else self.model.filter()
        return query.filter(
            subscriptions__isnull=False,
            subscriptions__routing_key__name=routing_key
        ).distinct()

    async def query_get_all(self):
        return self.model.all()


crud_user = CRUDUser(User)
