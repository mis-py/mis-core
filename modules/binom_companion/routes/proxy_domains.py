import loguru
from fastapi import APIRouter

from core.utils.schema import PageResponse, MisResponse

from ..schemas.proxy_domain import ProxyDomainModel, ProxyDomainCreateModel
from ..service import ProxyDomainService

router = APIRouter()


@router.get(
    '',
    response_model=PageResponse[ProxyDomainModel]
)
async def get_proxy_domains():
    return await ProxyDomainService().filter_and_paginate(
        # prefetch_related=['tracker_instance']
    )


@router.post(
    '/add',
    response_model=MisResponse[ProxyDomainModel]
)
async def create_proxy_domain(proxy_domain_in: ProxyDomainCreateModel):
    replacement_group = await ProxyDomainService().create(proxy_domain_in)

    # await replacement_group.fetch_related("tracker_instance")

    return MisResponse[ProxyDomainModel](result=replacement_group)


