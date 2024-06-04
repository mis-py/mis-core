from typing import Annotated

from fastapi import APIRouter, Security, Depends

from core.db.models import User, RoutingKey
from core.dependencies.misc import PaginateParamsDep
from core.dependencies.path import get_routing_key_by_id
from core.dependencies.security import get_current_user
from core.dependencies.services import get_routing_key_service, get_routing_key_subscription_service
from core.services.notification import RoutingKeySubscriptionService, \
    RoutingKeyService
from core.schemas.notification import RoutingKeyResponse, RoutingKeyUpdate, RoutingKeySubscriptionResponse
from core.utils.schema import MisResponse, PageResponse


router = APIRouter()


@router.get(
    '',
    response_model=PageResponse[RoutingKeyResponse]
)
async def get_all_notifications(
        routing_key_service: Annotated[RoutingKeyService, Depends(get_routing_key_service)],
        paginate_params: PaginateParamsDep,
):
    return await routing_key_service.filter_and_paginate(params=paginate_params)


@router.get(
    '/my',
    response_model=PageResponse[RoutingKeyResponse]
)
async def get_my_subscribes(
        routing_key_service: Annotated[RoutingKeyService, Depends(get_routing_key_service)],
        paginate_params: PaginateParamsDep,
        user: User = Depends(get_current_user)
):
    return await routing_key_service.filter_subscribed_and_paginate(
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
    response_model=MisResponse[RoutingKeySubscriptionResponse]
)
async def edit_my_subscribe(
        routing_key_subscription_service: Annotated[RoutingKeySubscriptionService, Depends(get_routing_key_subscription_service)],
        rk: RoutingKey = Depends(get_routing_key_by_id),
        user: User = Depends(get_current_user)
):
    subscription = await routing_key_subscription_service.subscribe(
        user_id=user.pk,
        routing_key_id=rk.pk,
    )
    return MisResponse[RoutingKeySubscriptionResponse](result=subscription)


@router.delete(
    '/unsubscribe',
    response_model=MisResponse
)
async def remove_my_subscribe(
        routing_key_subscription_service: Annotated[RoutingKeySubscriptionService, Depends(get_routing_key_subscription_service)],
        rk: RoutingKey = Depends(get_routing_key_by_id),
        user: User = Depends(get_current_user)
):
    await routing_key_subscription_service.unsubscribe(
        user_id=user.pk, routing_key_id=rk.pk,
    )
    return MisResponse()


@router.put(
    '/edit',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:notifications'])],
    response_model=MisResponse[RoutingKeyResponse]
)
async def edit_notification(
        routing_key_service: Annotated[RoutingKeyService, Depends(get_routing_key_service)],
        data: RoutingKeyUpdate,
        rk: RoutingKey = Depends(get_routing_key_by_id),
):
    await routing_key_service.update(id=rk.pk, schema_in=data)
    await routing_key_service.set_to_cache(rk=rk)

    return MisResponse[RoutingKeyResponse](result=rk)
