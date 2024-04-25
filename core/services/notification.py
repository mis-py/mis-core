from fastapi_pagination.bases import AbstractParams

from core.utils.schema import PageResponse
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from core.exceptions import AlreadyExists, NotFound


class RoutingKeyService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(uow.routing_key_repo)
        self.uow = uow

    async def filter_subscribed_and_paginate(self, user_id: int, params: AbstractParams) -> PageResponse:
        queryset = await self.uow.routing_key_repo.filter_by_user(user_id=user_id)
        return await self.uow.routing_key_repo.paginate(queryset=queryset, params=params)

    async def recreate(self, module_id, key: str, name: str):
        async with self.uow:
            # delete for remove user subscription relations
            await self.uow.routing_key_repo.delete(key=key)
            await self.uow.routing_key_repo.create(data={
                'app_id': module_id,
                'key': key,
                'name': name,
            })

    async def delete_unused(self, module_id: int, exist_keys: list[str]):
        return await self.uow.routing_key_repo.delete_unused(
            module_id=module_id,
            exist_keys=exist_keys,
        )


class RoutingKeySubscriptionService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(uow.routing_key_subscription_repo)
        self.uow = uow

    async def subscribe(self, user_id: int, routing_key_id: int):
        subscription = await self.get(user_id=user_id, routing_key_id=routing_key_id)
        if subscription is not None:
            raise AlreadyExists("Already subscribed")

        return await self.uow.routing_key_subscription_repo.create(
            data={"user_id": user_id, "routing_key_id": routing_key_id}
        )

    async def unsubscribe(self, user_id: int, routing_key_id: int):
        subscription = await self.get(user_id=user_id, routing_key_id=routing_key_id)
        if subscription is not None:
            raise NotFound("Not subscribed")

        await self.uow.routing_key_subscription_repo.delete(
            user_id=user_id, routing_key_id=routing_key_id,
        )

    # method delete all - set all new
    # async def set_user_subscriptions(self, user_id: int, routing_key_ids: list[int]):
    #     async with self.uow:
    #         # remove old subscriptions
    #         await self.uow.routing_key_subscription_repo.delete(user_id=user_id)
    #
    #         # set new subscriptions
    #         return await self.uow.routing_key_subscription_repo.create_bulk(
    #             user_id=user_id,
    #             routing_key_ids=routing_key_ids,
    #         )

