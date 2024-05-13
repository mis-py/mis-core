import loguru
from fastapi import APIRouter

from core.utils.schema import PageResponse, MisResponse

from ..schemas.proxy_domain import ProxyDomainModel, ProxyDomainCreateModel, ProxyDomainUpdateModel
from ..service import ProxyDomainService

router = APIRouter()


@router.get(
    '',
    response_model=PageResponse[ProxyDomainModel]
)
async def get_proxy_domains():
    return await ProxyDomainService().filter_and_paginate()


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
async def create_proxy_domain_bulk(proxy_domains_in: list[ProxyDomainCreateModel]):
    proxy_domains = await ProxyDomainService().create_bulk(proxy_domains_in)
    loguru.logger.debug(proxy_domains[0])
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


@router.delete(
    '/remove',
    response_model=MisResponse
)
async def delete_proxy_domain(proxy_domain_id: int):
    await ProxyDomainService().delete(id=proxy_domain_id)

    return MisResponse()
