from fastapi_pagination.bases import AbstractParams
from tortoise.queryset import QuerySet

from core.crud import user
from core.utils.notification.recipient import Recipient
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


async def query_users_who_receive_message(routing_key: str, is_force_send: bool, recipient: Recipient) -> QuerySet:
    if not recipient and not is_force_send:
        return await user.query_get_by_subscription(routing_key)

    if is_force_send and not recipient:
        return await user.query_get_all()

    if recipient.type == Recipient.Type.USER:
        query = await user.query_get_multi(id=recipient.user_id)
    elif recipient.type == Recipient.Type.TEAM:
        query = await user.query_get_multi(team_id=recipient.team_id)
    else:
        raise Exception(f'Recipient type {recipient.type} not exist or not implement')

    if is_force_send and recipient:
        return query

    return await user.query_get_by_subscription(query=query, routing_key=routing_key)