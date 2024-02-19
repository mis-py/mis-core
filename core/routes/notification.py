from fastapi import APIRouter, Security, Depends, Response


from core.db.models import User, RoutingKey


# from core.dependencies import get_current_user

from core.dependencies.path import get_routing_key_by_id, PaginationDep
from core.dependencies.security import get_current_user
from core.services.notification import subscribe_routing_key, unsubscribe_routing_key
from core.utils.notification import routing_key_to_dict
from core.schemas.notification import RoutingKeyModel, EditRoutingKey
from services.redis import RedisService

from core.crud.notification import routing_key, subscription

router = APIRouter()


@router.get('/routing_keys', response_model=list[RoutingKeyModel])
async def get_routing_keys(pagination: PaginationDep, user: User = Depends(get_current_user)):
    query_routing_keys = await routing_key.query_get_multi_with_select(**pagination)
    subscribed_names = await routing_key.key_list_by_user(user)

    routing_keys = await RoutingKeyModel.from_queryset(query_routing_keys)
    for rk in routing_keys:
        # set is_subscribed=True if current user subscribed on routing key
        if rk.name in subscribed_names:
            rk.is_subscribed = True

    return routing_keys


@router.get('/routing_keys/my', response_model=list[RoutingKeyModel])
async def get_my_subscriptions_routing_keys(pagination: PaginationDep, user: User = Depends(get_current_user)):
    return await routing_key.get_subscribed_by_user(**pagination, user=user)


@router.post('/routing_keys/subscribe')
async def set_routing_key_subscriptions(routing_key_ids: list[int], user: User = Depends(get_current_user)):
    return await subscription.set_user_subscriptions(user=user, routing_key_ids=routing_key_ids)


@router.put('/routing_keys', dependencies=[Security(get_current_user, scopes=['core:sudo'])])
async def edit_routing_key(data: EditRoutingKey, rk: RoutingKey = Depends(get_routing_key_by_id)):
    await routing_key.update(rk, data)

    # set/update value in cache
    await RedisService.cache.set_json(
        cache_name="routing_key",
        key=rk.name,
        value=routing_key_to_dict(rk),
    )
    return rk


@router.post('/routing_keys')
async def routing_key_subscribe(rk: RoutingKey = Depends(get_routing_key_by_id), user: User = Depends(get_current_user)):
    await subscribe_routing_key(user, rk)
    return Response(status_code=200)


@router.delete('/routing_keys')
async def routing_key_unsubscribe(rk: RoutingKey = Depends(get_routing_key_by_id), user: User = Depends(get_current_user)):
    await unsubscribe_routing_key(user, rk)
    return Response(status_code=200)
