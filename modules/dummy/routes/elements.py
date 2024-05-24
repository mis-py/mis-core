from typing import Annotated

from fastapi import APIRouter, Depends

from core.dependencies.misc import PaginateParamsDep
from core.utils.schema import MisResponse, PageResponse
from modules.dummy.dependencies.services import get_element_service
from modules.dummy.schemas.elements import DummyElementRead, DummyElementUpdate
from modules.dummy.services.dummy_element import DummyElementService

router = APIRouter()


@router.get(
    "/get", response_model=PageResponse[DummyElementRead],
)
async def get_list_elements(
        dummy_element_service: Annotated[DummyElementService, Depends(get_element_service)],
        paginate_params: PaginateParamsDep,
):
    return await dummy_element_service.filter_and_paginate(params=paginate_params)


@router.put(
    "/update-bulk", response_model=MisResponse[list[DummyElementRead]],
)
async def update_bulk_elements(
        dummy_element_service: Annotated[DummyElementService, Depends(get_element_service)],
        elements_in: list[DummyElementUpdate],
):
    updated_elements = await dummy_element_service.update_bulk(elements_in)
    return MisResponse[list[DummyElementRead]](result=updated_elements)
