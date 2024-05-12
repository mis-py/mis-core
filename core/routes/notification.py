from fastapi import APIRouter, Security, Depends

from core.db.models import User, RoutingKey
from core.dependencies.misc import PaginateParamsDep
from core.dependencies.uow import UnitOfWorkDep
from core.dependencies.path import get_routing_key_by_id
from core.dependencies.security import get_current_user
from core.repositories.routing_key import RoutingKeyRepository
from core.services.notification import RoutingKeySubscriptionService, \
    RoutingKeyService
from core.schemas.notification import RoutingKeyResponse, RoutingKeyUpdate
from core.utils.notification.utils import routing_key_to_dict
from core.utils.schema import MisResponse, PageResponse
from libs.redis import RedisService


router = APIRouter()


@router.get(
    '',
    response_model=PageResponse[RoutingKeyResponse]
)
async def get_all_notifications(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
):
    return await RoutingKeyService(uow).filter_and_paginate(params=paginate_params)


@router.get(
    '/my',
    response_model=PageResponse[RoutingKeyResponse]
)
async def get_my_subscribes(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
        user: User = Depends(get_current_user)
):
    return await RoutingKeyService(uow).filter_subscribed_and_paginate(
        user_id=user.pk,
        params=paginate_params,
    )


# @router.post(
#     '/my',
#     response_model=MisResponse[list[RoutingKeyResponse]]
# )
# async def edit_my_subscribes(
#         uow: UnitOfWorkDep,
#         routing_key_ids: list[int],
#         user: User = Depends(get_current_user),
# ):
#     subscriptions = await RoutingKeySubscriptionService(uow).set_user_subscriptions(user_id=user.pk, routing_key_ids=routing_key_ids)
#
#     return MisResponse[RoutingKeyResponse](result=subscriptions)

@router.post(
    '/subscribe',
    response_model=MisResponse[RoutingKeyResponse]
)
async def edit_my_subscribe(
        uow: UnitOfWorkDep,
        rk: RoutingKey = Depends(get_routing_key_by_id),
        user: User = Depends(get_current_user)
):
    subscription = await RoutingKeySubscriptionService(uow).subscribe(
        user_id=user.pk,
        routing_key_id=rk.pk
    )
    return MisResponse[RoutingKeyResponse](result=subscription)


@router.delete(
    '/unsubscribe',
    response_model=MisResponse
)
async def remove_my_subscribe(
        uow: UnitOfWorkDep,
        rk: RoutingKey = Depends(get_routing_key_by_id),
        user: User = Depends(get_current_user)
):
    await RoutingKeySubscriptionService(uow).unsubscribe(
        user_id=user.pk, routing_key_id=rk.pk,
    )
    return MisResponse()


@router.put(
    '/edit',
    dependencies=[Security(get_current_user, scopes=['core:sudo'])],
    response_model=MisResponse[RoutingKeyResponse]
)
async def edit_notification(
        uow: UnitOfWorkDep,
        data: RoutingKeyUpdate,
        rk: RoutingKey = Depends(get_routing_key_by_id),
):
    await RoutingKeyRepository(uow).update(id=rk.pk, data=data.model_dump())

    # set/update value in cache
    await RedisService.cache.set_json(
        cache_name="routing_key",
        key=rk.name,
        value=routing_key_to_dict(rk),
    )
    return MisResponse[RoutingKeyResponse](result=rk)
