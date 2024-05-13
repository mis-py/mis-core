from abc import ABC, abstractmethod

from core.db.models import RoutingKeySubscription
from core.repositories.base.repository import TortoiseORMRepository, IRepository


class IRoutingKeySubscriptionRepository(IRepository, ABC):
    @abstractmethod
    async def create_bulk(self, **kwargs):
        raise NotImplementedError


class RoutingKeySubscriptionRepository(TortoiseORMRepository, IRoutingKeySubscriptionRepository):
    model = RoutingKeySubscription

    async def create_bulk(self, user_id: int, routing_key_ids: list[int]):
        objects = []
        for routing_key_id in routing_key_ids:
            objects.append(RoutingKeySubscription(
                routing_key_id=routing_key_id,
                user_id=user_id,
            ))
        return await self.model.bulk_create(objects=objects, ignore_conflicts=True)
