from typing import Annotated

from fastapi import APIRouter, Depends, Body

from core.dependencies.misc import PaginateParamsDep
from core.utils.schema import MisResponse, PageResponse
from modules.dummy.dependencies.services import get_element_service, get_category_service
from modules.dummy.schemas.elements import DummyElementRead, DummyElementUpdate
from modules.dummy.services.dummy_category import DummyCategoryService
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


@router.put(
    "/set-visible", response_model=MisResponse[list[DummyElementRead]],
)
async def set_visible_by_category(
        dummy_element_service: Annotated[DummyElementService, Depends(get_element_service)],
        dummy_category_service: Annotated[DummyCategoryService, Depends(get_category_service)],
        category_id: int = Body(),
        is_visible: bool = Body(),
):
    # category_id check exists
    await dummy_category_service.get_or_raise(id=category_id)

    updated_elements = await dummy_element_service.set_visible_by_category(
        category_id=category_id,
        is_visible=is_visible,
    )
    return MisResponse[list[DummyElementRead]](result=updated_elements)
