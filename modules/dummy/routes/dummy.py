from typing import Annotated

from fastapi import APIRouter, Security, Depends

from core.dependencies.misc import RoutingKeysDep
from core.dependencies.module import get_app_context
from core.dependencies.security import get_current_user
from core.utils.schema import MisResponse, PageResponse
from core.utils.app_context import AppContext

from ..db.schema import DummyResponse, DummyCreate, DummyEdit, DummyDataResponse
from ..dependencies.services import get_dummy_model_service
from ..services.dummy import DummyService

router = APIRouter()

restricted_router = APIRouter(
    dependencies=[Security(get_current_user, scopes=['dummy:sudo'])],
)


@restricted_router.get(
    '',
    response_model=PageResponse[DummyResponse]
)
async def get_paginated_dummies(
        dummy_model_service: Annotated[DummyService, Depends(get_dummy_model_service)],
):
    return await dummy_model_service.filter_and_paginate()


@restricted_router.post(
    '/add',
    response_model=MisResponse[DummyResponse]
)
async def create_dummy(
        dummy_model_service: Annotated[DummyService, Depends(get_dummy_model_service)],
        dummy_in: DummyCreate,
):
    new_dummy = await dummy_model_service.create(dummy_in)
    return MisResponse[DummyResponse](result=new_dummy)


@restricted_router.put(
    '/edit',
    response_model=MisResponse[DummyResponse]
)
async def edit_dummy(
        dummy_model_service: Annotated[DummyService, Depends(get_dummy_model_service)],
        dummy_id: int,
        dummy_in: DummyEdit
):
    edited_dummy = await dummy_model_service.update(dummy_id, dummy_in)
    return MisResponse[DummyResponse](result=edited_dummy)


@restricted_router.delete(
    '/remove',
    response_model=MisResponse
)
async def delete_dummy(
        dummy_model_service: Annotated[DummyService, Depends(get_dummy_model_service)],
        dummy_id: int,
):
    await dummy_model_service.delete(id=dummy_id)

    return MisResponse()


@router.get('/get_dummy_data', response_model=MisResponse[DummyDataResponse])
async def get_dummy_data(
        dummy_model_service: Annotated[DummyService, Depends(get_dummy_model_service)],
        routing_keys: RoutingKeysDep,
        ctx: Annotated[AppContext, Depends(get_app_context)],
):
    dummy_list = await dummy_model_service.filter()

    response = DummyDataResponse(
        current_user=ctx.user,
        current_team=ctx.team,
        test_data=dummy_list,
        variable=ctx.variables.PRIVATE_SETTING,
        module=ctx.module.name,
        routing_keys=[routing_keys.DUMMY_EVENT, routing_keys.DUMMY_MANUAL_EVENT],
    )
    return MisResponse[DummyDataResponse](result=response)


