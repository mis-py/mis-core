from tortoise.queryset import QuerySet

from core.db.models import User
from core.crud.base import CRUDBase, CreateSchemaType, UpdateSchemaType
from core.auth_backend import set_password


class CRUDUser(CRUDBase):
    async def create(self, obj_in: CreateSchemaType) -> User:
        """Create user with password"""
        new_user = User(
            username=obj_in.username,
            team_id=obj_in.team_id,
            position=obj_in.position,
        )
        set_password(new_user, obj_in.password)
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
            set_password(user, new_password)

        await user.update_from_dict(update_data).save()
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

    async def get_from_ids(self, ids: list[int]) -> list[User]:
        return await self.model.filter(id__in=ids)


user = CRUDUser(User)
