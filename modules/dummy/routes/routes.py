from fastapi import APIRouter, Depends, Request
from core.utils.schema import MisResponse


from ..db import DummyModel, DummyModelSchema, DummyListModelSchema

from .schemas import DummyResponse

from core.schemas.common import UserModelShort
from core.dependencies.variables import VariablesDep

router = APIRouter()


@router.get('/get_all')
async def get_all():
    return await DummyModelSchema.from_queryset(DummyModel.all())


@router.post('/create_new')
async def create_new(new_string: str):
    new = await DummyModel.create(dummy_string=new_string)
    return await DummyModelSchema.from_tortoise_orm(new)


@router.get('/get_dummy_data', response_model=DummyResponse)
async def get_dummy_data(
        request: Request,
        variables: VariablesDep
):

    schema = await DummyListModelSchema.from_queryset(DummyModel.all())

    response = DummyResponse(
        current_user=await UserModelShort.from_tortoise_orm(request.state.current_user),
        test_data=schema.model_dump(),
        setting=variables.PRIVATE_SETTING
    )
    return response


