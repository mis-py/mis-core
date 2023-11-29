from fastapi import APIRouter, Depends, Request
from loguru import logger


from ..db import DummyModel, DummyModelSchema, DummyListModelSchema

from .schemas import DummyResponse

from core.db.schemas import UserModelShort
from core.dependencies.settings import get_settings_proxy
from services.modules.components import APIRoutes
from services.variables.variables import SettingsProxy
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
        settings_proxy: SettingsProxy = Depends(get_settings_proxy)
):

    schema = await DummyListModelSchema.from_queryset(DummyModel.all())

    response = DummyResponse(
        current_user=await UserModelShort.from_tortoise_orm(request.state.current_user),
        test_data=schema.model_dump(),
        setting=settings_proxy.PRIVATE_SETTING
    )
    return response


routes = APIRoutes(router)
