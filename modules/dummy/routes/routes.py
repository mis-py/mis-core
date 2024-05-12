from fastapi import APIRouter, Security

from core.dependencies.security import get_current_user
from core.utils.schema import MisResponse, PageResponse

from ..db.schema import DummyResponse, DummyCreate, DummyEdit
from ..service import DummyService

router = APIRouter()

restricted_router = APIRouter(
    dependencies=[Security(get_current_user, scopes=['dummy:sudo'])],
)


@restricted_router.get(
    '',
    response_model=PageResponse[DummyResponse]
)
async def get_paginated_dummies():
    return await DummyService().filter_and_paginate()


@restricted_router.post(
    '/add',
    response_model=MisResponse[DummyResponse]
)
async def create_dummy(dummy_in: DummyCreate):
    new_dummy = await DummyService().create(dummy_in)
    return MisResponse[DummyResponse](result=new_dummy)


@restricted_router.put(
    '/edit',
    response_model=MisResponse[DummyResponse]
)
async def edit_dummy(
        dummy_id: int,
        dummy_in: DummyEdit
):
    edited_dummy = await DummyService().update(dummy_id, dummy_in)
    return MisResponse[DummyResponse](result=edited_dummy)


@restricted_router.delete(
    '/remove',
    response_model=MisResponse
)
async def delete_dummy(dummy_id: int):
    await DummyService().delete(id=dummy_id)

    return MisResponse()

# todo examples with dependencies varioables, user, team, model etc
# @router.get('/get_dummy_data', response_model=DummyResponse)
# async def get_dummy_data(
#         request: Request,
#         variables: VariablesDep
# ):
#
#     schema = await DummyListModelSchema.from_queryset(DummyModel.all())
#
#     response = DummyResponse(
#         current_user=await UserModelShort.from_tortoise_orm(request.state.current_user),
#         test_data=schema.model_dump(),
#         setting=variables.PRIVATE_SETTING
#     )
#     return response


