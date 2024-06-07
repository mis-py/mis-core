from typing import Annotated

from fastapi import APIRouter, Security, Query, Depends
from loguru import logger


from core.utils.schema import PageResponse, MisResponse
from core.dependencies.security import get_current_user
from core.dependencies.module import get_app_context
from core.utils.module import AppContext

from ..schemas.proxy_domain import (
    ProxyDomainModel,
    ProxyDomainCreateModel,
    ProxyDomainUpdateModel,
    ProxyDomainServerNameModels,
    ProxyDomainCreateBulkModel,
    ProxyDomainBulkUpdateModel
)
from ..service import ProxyDomainService, ReplacementGroupService

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=[
        'binom_companion:sudo',
        'binom_companion:proxy_domains'
    ])],
)


@router.get(
    '',
    response_model=PageResponse[ProxyDomainModel]
)
async def get_proxy_domains():
    return await ProxyDomainService().filter_and_paginate(prefetch_related=['tracker_instance'])


@router.post(
    '/add',
    response_model=MisResponse[ProxyDomainModel]
)
async def create_proxy_domain(proxy_domain_in: ProxyDomainCreateModel):
    proxy_domain = await ProxyDomainService().create(proxy_domain_in)

    return MisResponse[ProxyDomainModel](result=proxy_domain)


@router.post(
    '/add_bulk',
    response_model=MisResponse[list[ProxyDomainModel]])
async def create_proxy_domain_bulk(
        proxy_domains_in: ProxyDomainCreateBulkModel,
        ctx: Annotated[AppContext, Depends(get_app_context)]
):
    proxy_domains = await ProxyDomainService().create_bulk(proxy_domains_in, ctx)

    return MisResponse[list[ProxyDomainModel]](result=proxy_domains)


@router.put(
    '/edit',
    response_model=MisResponse[ProxyDomainModel]
)
async def edit_proxy_domain(
        proxy_domain_id: int,
        proxy_domain_in: ProxyDomainUpdateModel,
):
    proxy_domain = await ProxyDomainService().update(
        id=proxy_domain_id,
        schema_in=proxy_domain_in
    )

    return MisResponse[ProxyDomainModel](result=proxy_domain)


@router.put(
    '/edit_bulk',
    response_model=MisResponse[ProxyDomainModel]
)
async def edit_bulk_proxy_domain(
        proxy_domains_in: ProxyDomainBulkUpdateModel,
):
    proxy_domain = await ProxyDomainService().update_bulk(proxy_domains_in)

    return MisResponse[ProxyDomainModel](result=proxy_domain)


@router.delete(
    '/remove',
    response_model=MisResponse
)
async def delete_proxy_domain(proxy_domain_id: int):
    await ProxyDomainService().delete(id=proxy_domain_id)

    return MisResponse()


@router.get(
    '/get_server_names',
    response_model=MisResponse[ProxyDomainServerNameModels]
)
async def get_server_names():
    server_names = await ProxyDomainService().get_server_names()
    return MisResponse[ProxyDomainServerNameModels](result=server_names)


@router.get(
    '/get_available_proxy_domains_for_groups',
    response_model=MisResponse[list[ProxyDomainModel]]
)
async def get_available_proxy_domains_for_groups(
        replacement_group_ids: list[int] = Query(),
):
    groups = await ReplacementGroupService().get_groups_from_id(replacement_group_ids)
    domains_set = await ProxyDomainService().find_intersection(groups)

    return MisResponse[list[ProxyDomainModel]](result=domains_set)
