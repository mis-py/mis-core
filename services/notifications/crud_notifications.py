from core.db import RoutingKey, User, RoutingKeySubscription
from core.db.crud.base import CRUDBase


class CRUDRoutingKeys(CRUDBase):
    async def query_get_multi_with_select(self, skip: int, limit: int):
        """Get ordered and selected queryset"""
        query = await self.query_get_multi(skip=skip, limit=limit)
        return query.order_by("app_id").select_related("app")

    async def get_subscribed_by_user(self, skip: int, limit: int, user: User) -> list[RoutingKey]:
        """Get routing keys objects subscribed by user"""
        query = await self.query_get_multi(skip=skip, limit=limit, key_subscriptions__user=user)
        return await query.order_by("app_id").select_related("app")

    async def get_by_name(self, name: str):
        return await self.get(name=name)

    async def key_list_by_user(self, user: User):
        """Get list names of routing keys subscribed by user"""
        query = await self.query_get_multi(key_subscriptions__user=user)
        return await query.values_list('name', flat=True)

    async def all_keys_values_list(self) -> list[tuple[str, str]]:
        return await self.model.all().values_list('name', 'app__name')

    async def remove_routing_keys_by_app(self, app_model, routing_keys):
        return await self.model.filter(app=app_model) \
            .exclude(name__in=routing_keys) \
            .delete()



routing_key = CRUDRoutingKeys(RoutingKey)


class CRUDRoutingKeySubscription(CRUDBase):
    async def get_or_create_subscription(
            self, user: User, routing_key: RoutingKey
    ) -> tuple[RoutingKeySubscription, bool]:
        return await self.model.get_or_create(
            user=user, routing_key=routing_key
        )

    async def set_user_subscriptions(self, user: User, routing_key_ids: list[int]):
        # remove old subscriptions
        await self.remove_list(user=user)

        # set new subscriptions
        for routing_key in await RoutingKey.filter(id__in=routing_key_ids):
            await self.model.get_or_create(
                user=user, routing_key=routing_key
            )


subscription = CRUDRoutingKeySubscription(RoutingKeySubscription)
