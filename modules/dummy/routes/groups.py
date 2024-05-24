from typing import Annotated

from fastapi import APIRouter, Depends

from core.dependencies.misc import PaginateParamsDep
from core.utils.schema import MisResponse, PageResponse
from modules.dummy.dependencies.services import get_group_service, get_category_service, get_element_service
from modules.dummy.schemas.groups import DummyGroupRead
from modules.dummy.services.dummy_category import DummyCategoryService
from modules.dummy.services.dummy_element import DummyElementService
from modules.dummy.services.dummy_group import DummyGroupService

router = APIRouter()


@router.post(
    "/fill-data",
)
async def create_test_group_category_and_elements(
        dummy_group_service: Annotated[DummyGroupService, Depends(get_group_service)],
        dummy_category_service: Annotated[DummyCategoryService, Depends(get_category_service)],
        dummy_element_service: Annotated[DummyElementService, Depends(get_element_service)],
):
    group_name = 'Group TEST'
    group = await dummy_group_service.get(name=group_name)
    if not group:
        group = await dummy_group_service.create_by_kwargs(name=group_name)

    category_name = 'Category TEST'
    category = await dummy_category_service.get(name=category_name)
    if not category:
        category = await dummy_category_service.create_by_kwargs(name=category_name, group_id=group.pk)

    for element_num in range(1, 5):
        element_name = f'Element TEST {element_num}'
        element = await dummy_element_service.get(name=element_name)
        if element:
            continue
        await dummy_element_service.create_by_kwargs(name=element_name, category_id=category.pk)

    return MisResponse()


@router.get(
    "/get-simple", response_model=PageResponse[DummyGroupRead]
)
async def get_groups_with_simple_prefetch(
        dummy_group_service: Annotated[DummyGroupService, Depends(get_group_service)],
        paginate_params: PaginateParamsDep,
):
    return await dummy_group_service.filter_and_paginate(
        prefetch_related=['categories__elements'],
        params=paginate_params,
    )


@router.get(
    "/get-custom", response_model=PageResponse[DummyGroupRead]
)
async def get_groups_with_custom_prefetch(
        dummy_group_service: Annotated[DummyGroupService, Depends(get_group_service)],
        paginate_params: PaginateParamsDep,
):
    return await dummy_group_service.filter_with_elements_and_paginate(params=paginate_params)
