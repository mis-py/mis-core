import loguru
from fastapi import APIRouter, Security

from core.dependencies.misc import AppContextDep
from core.dependencies.security import get_current_user
from core.utils.schema import PageResponse, MisResponse

from ..schemas.replacement_group import ReplacementGroupModel, ReplacementGroupCreateModel, ReplacementGroupUpdateModel, \
    ReplacementGroupChangeProxyIds
from ..service import ReplacementGroupService

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'binom_companion:replacement_groups'])],
)


@router.get(
    '',
    response_model=PageResponse[ReplacementGroupModel]
)
async def get_replacement_groups():
    return await ReplacementGroupService().filter_and_paginate(
        prefetch_related=[
            'replacement_history'
        ]
    )


@router.post(
    '/add',
    response_model=MisResponse[ReplacementGroupModel]
)
async def create_replacement_group(replacement_group_in: ReplacementGroupCreateModel):
    replacement_group = await ReplacementGroupService().create(replacement_group_in)

    await replacement_group.fetch_related("replacement_history")

    return MisResponse[ReplacementGroupModel](result=replacement_group)


@router.get(
    '/get',
    response_model=MisResponse[ReplacementGroupModel]
)
async def get_replacement_group(replacement_group_id: int):
    replacement_group = await ReplacementGroupService().get(
        id=replacement_group_id,
        prefetch_related=[
            'replacement_history'
        ]
    )

    return MisResponse[ReplacementGroupModel](result=replacement_group)


@router.put(
    '/edit',
    response_model=MisResponse[ReplacementGroupModel]
)
async def edit_replacement_group(
        replacement_group_id: int,
        replacement_group_in: ReplacementGroupUpdateModel,
):
    replacement_group = await ReplacementGroupService().update(
        id=replacement_group_id,
        schema_in=replacement_group_in
    )

    await replacement_group.fetch_related("replacement_history")

    return MisResponse[ReplacementGroupModel](result=replacement_group)


@router.delete(
    '/remove',
    response_model=MisResponse
)
async def delete_replacement_group(replacement_group_id: int):
    await ReplacementGroupService().delete(id=replacement_group_id)

    return MisResponse()


@router.get(
    '/check',
    response_model=MisResponse[dict]
)
async def check_fetch_replacement_group(replacement_group_id: int):
    check_result = await ReplacementGroupService().check_replacement_group(replacement_group_id)

    return MisResponse[dict](result=check_result)


@router.post(
    '/change_proxy',
    response_model=MisResponse
)
async def change_proxy_domain(
    replacement_group_ids: ReplacementGroupChangeProxyIds,
    ctx: AppContextDep
):
    await ReplacementGroupService().proxy_change(
        ctx,
        replacement_group_ids.replacement_group_ids,
        "Changed via endpoint"
    )

    return MisResponse
