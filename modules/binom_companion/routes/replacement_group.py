from typing import Annotated

from fastapi import APIRouter, Security, Query, Depends

from core.dependencies.misc import PaginateParamsDep
from core.dependencies.context import get_app_context
from core.dependencies.security import get_current_user
from core.utils.schema import PageResponse, MisResponse
from core.utils.app_context import AppContext

from ..schemas.replacement_group import ReplacementGroupModel, ReplacementGroupCreateModel, ReplacementGroupUpdateModel, \
    ReplacementGroupChangeProxyIds, ReplacementGroupFakeChangeProxyIds
from ..schemas.replacement_group_with_history import ReplacementGroupWithHistory
from ..service import ReplacementGroupService

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=[
        'binom_companion:sudo',
        'binom_companion:replacement_groups'
    ])],
)


@router.get(
    '',
    response_model=PageResponse[ReplacementGroupWithHistory]
)
async def get_replacement_groups(
        paginate_params: PaginateParamsDep,
        history_limit: int = Query(default=10),
        is_active: bool | None = None,
):
    return await ReplacementGroupService().filter_with_history_and_paginate(
        history_limit=history_limit,
        params=paginate_params,
        is_active=is_active
    )


@router.post(
    '/add',
    response_model=MisResponse[ReplacementGroupModel]
)
async def create_replacement_group(replacement_group_in: ReplacementGroupCreateModel):
    replacement_group = await ReplacementGroupService().create(replacement_group_in)

    await replacement_group.fetch_related("tracker_instance")

    return MisResponse[ReplacementGroupModel](result=replacement_group)


@router.get(
    '/get',
    response_model=MisResponse[ReplacementGroupWithHistory]
)
async def get_replacement_group(
        replacement_group_id: int,
        history_limit: int = Query(default=10),
):
    replacement_group = await ReplacementGroupService().get_with_history(
        id=replacement_group_id,
        history_limit=history_limit,
    )
    return MisResponse[ReplacementGroupWithHistory](result=replacement_group)


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

    await replacement_group.fetch_related("tracker_instance")

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
    response_model=MisResponse[dict]
)
async def change_proxy_domain(
    replacement_group_ids: ReplacementGroupChangeProxyIds,
    ctx: Annotated[AppContext, Depends(get_app_context)]
):
    change_result = await ReplacementGroupService().proxy_change(
        ctx,
        replacement_group_ids.replacement_group_ids,
        "Changed by user"
    )

    return MisResponse[dict](result=change_result)


@router.get(
    '/check_domains',
    response_model=MisResponse[list]
)
async def check_domains_replacement_group(
        replacement_group_ids: Annotated[list[int], Query()] = None,
        proxy_ids: Annotated[list[int], Query()] = None,
):
    check_result = await ReplacementGroupService().check_group_domains(
        replacement_group_ids=replacement_group_ids,
        proxy_ids=proxy_ids,
    )
    return MisResponse[list](result=check_result)


@router.post(
    '/add_history',
    response_model=MisResponse[dict]
)
async def add_history_domain(
        schema_in: ReplacementGroupFakeChangeProxyIds,
        ctx: Annotated[AppContext, Depends(get_app_context)],
):
    change_result = await ReplacementGroupService().fake_proxy_change(
        ctx=ctx,
        replacement_group_ids=schema_in.replacement_group_ids,
        reason="Changed by user (fake)",
        domains=schema_in.domains,
        servers=schema_in.servers,
    )

    return MisResponse[dict](result=change_result)
