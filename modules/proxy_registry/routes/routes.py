from typing import Annotated

from fastapi import APIRouter, Depends, Security, Request
from starlette import status

from core.dependencies.misc import PaginateParamsDep
from core.utils.schema import PageResponse, MisResponse
from libs.redis import RedisService
from modules.proxy_registry.db.models import Proxy
from modules.proxy_registry.schemas.proxy import ProxyRead, ProxyCheck, ProxyCheckURL, ProxyReadSingle, ProxyCreate, \
    ProxyUpdate
from modules.proxy_registry.dependencies.path import get_proxy_by_id
from modules.proxy_registry.dependencies.services import get_proxy_service
from modules.proxy_registry.services.proxy import ProxyService
from modules.proxy_registry.services.util import check_proxy_id_by_ipify, check_proxy_address_by_ipify, change_proxy_ip, \
    restore_last_ip_from_redis

from core.dependencies.security import get_current_user

router = APIRouter(
    prefix='/proxies',
    dependencies=[Security(get_current_user, scopes=['proxy:sudo', 'proxy:proxies'])]
)


@router.get('/', response_model=PageResponse[ProxyRead])
async def get_proxy_list(
        proxy_service: Annotated[ProxyService, Depends(get_proxy_service)],
        paginate_params: PaginateParamsDep,
        request: Request,
):
    proxies = await proxy_service.filter_and_paginate(params=paginate_params)

    await restore_last_ip_from_redis(proxies.result.items, redis=RedisService())

    return proxies


@router.post('/check', response_model=MisResponse[ProxyCheck])
async def check_proxy(
        proxy_service: Annotated[ProxyService, Depends(get_proxy_service)],
        request: Request,
        proxy_data: ProxyCheckURL,
):
    result = None

    if proxy_data.proxy_address:
        result = await check_proxy_address_by_ipify(proxy_data.proxy_address)
    elif proxy_data.id:
        proxy = await proxy_service.get(id=proxy_data.id)
        result = await check_proxy_id_by_ipify(proxy, RedisService())

    return MisResponse[ProxyCheck](result=result)


@router.post('/change-status', response_model=MisResponse[ProxyReadSingle])
async def change_status(
        proxy_service: Annotated[ProxyService, Depends(get_proxy_service)],
        proxy: Proxy = Depends(get_proxy_by_id),
):
    proxy = await proxy_service.toggle_is_enabled(proxy_id=proxy.pk, current_is_enabled=proxy.is_enabled)
    return MisResponse[ProxyReadSingle](result=proxy)


@router.post('/change-ip/', response_model=MisResponse[ProxyCheck])
async def change_proxy(request: Request, proxy: Proxy = Depends(get_proxy_by_id)):
    result = await change_proxy_ip(proxy, RedisService())
    return MisResponse[ProxyCheck](result=result)


@router.post('/add', response_model=MisResponse[ProxyRead])
async def create_proxy(
        proxy_service: Annotated[ProxyService, Depends(get_proxy_service)],
        create_data: ProxyCreate,
):
    proxy = await proxy_service.create(schema_in=create_data)
    return MisResponse[ProxyRead](result=proxy)


@router.get('/get', response_model=MisResponse[ProxyReadSingle])
async def get_proxy(proxy: Proxy = Depends(get_proxy_by_id)):
    return MisResponse[ProxyReadSingle](result=proxy)


@router.put('/edit', response_model=MisResponse[ProxyRead])
async def update_proxy(
        proxy_service: Annotated[ProxyService, Depends(get_proxy_service)],
        update_data: ProxyUpdate,
        proxy: Proxy = Depends(get_proxy_by_id),
):
    proxy = await proxy_service.update(id=proxy.pk, schema_in=update_data)
    return MisResponse[ProxyRead](result=proxy)


@router.delete('/remove')
async def del_proxy(
        proxy_service: Annotated[ProxyService, Depends(get_proxy_service)],
        proxy: Proxy = Depends(get_proxy_by_id),
):
    await proxy_service.delete(id=proxy.pk)
    return MisResponse(status_code=status.HTTP_204_NO_CONTENT)
