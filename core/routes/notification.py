from fastapi import APIRouter, Security, Depends, Response
from fastapi_pagination import Page

from core.db.models import User, RoutingKey
from core.dependencies.misc import UnitOfWorkDep, PaginateParamsDep

# from core.dependencies import get_current_user

from core.dependencies.path import get_routing_key_by_id, PaginationDep
from core.dependencies.security import get_current_user
from core.exceptions import AlreadyExists
from core.services.notification import RoutingKeySubscriptionService, \
    RoutingKeyService
from core.schemas.notification import RoutingKeyResponse, RoutingKeyUpdate
from core.utils.notification.utils import routing_key_to_dict
from services.redis import RedisService

from core.crud.notification import routing_key, subscription

router = APIRouter()


@router.get('/routing_keys', response_model=Page[RoutingKeyResponse])
async def get_routing_keys(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
        user: User = Depends(get_current_user),
):
    return await RoutingKeyService(uow).filter_and_paginate(params=paginate_params)


@router.get('/routing_keys/my', response_model=Page[RoutingKeyResponse])
async def get_my_subscriptions_routing_keys(
        uow: UnitOfWorkDep,
        paginate_params: PaginateParamsDep,
        user: User = Depends(get_current_user)
):
    return await RoutingKeyService(uow).filter_subscribed_and_paginate(
        user_id=user.pk,
        params=paginate_params,
    )


@router.post('/routing_keys/subscribe')
async def set_routing_key_subscriptions(
        uow: UnitOfWorkDep,
        routing_key_ids: list[int],
        user: User = Depends(get_current_user),
):
    return await RoutingKeySubscriptionService(uow).set_user_subscriptions(user=user, routing_key_ids=routing_key_ids)


@router.put('/routing_keys', dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def edit_routing_key(data: RoutingKeyUpdate, rk: RoutingKey = Depends(get_routing_key_by_id)):
    await routing_key.update(rk, data)

    # set/update value in cache
    await RedisService.cache.set_json(
        cache_name="routing_key",
        key=rk.name,
        value=routing_key_to_dict(rk),
    )
    return rk


@router.post('/routing_keys')
async def routing_key_subscribe(
        uow: UnitOfWorkDep,
        rk: RoutingKey = Depends(get_routing_key_by_id),
        user: User = Depends(get_current_user)
):
    subscription = await RoutingKeySubscriptionService(uow).get(user_id=user.pk, routing_key_id=rk.pk)
    if subscription is not None:
        raise AlreadyExists("Already subscribed")

    await RoutingKeySubscriptionService(uow).subscribe(
        user_id=user.pk,
        routing_key_id=rk.pk
    )
    return Response(status_code=200)


@router.delete('/routing_keys')
async def routing_key_unsubscribe(
        uow: UnitOfWorkDep,
        rk: RoutingKey = Depends(get_routing_key_by_id),
        user: User = Depends(get_current_user)
):
    await RoutingKeySubscriptionService(uow).unsubscribe(
        user_id=user.pk, routing_key_id=rk.pk,
    )
    return Response(status_code=200)
