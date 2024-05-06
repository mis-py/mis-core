import logging

from fastapi import APIRouter, Depends, Response, Security, Request
from fastapi.responses import JSONResponse

from modules.core.dependencies import get_current_active_user
from modules.core.dependencies.path import PaginationDep
from modules.proxy.db import crud
from modules.proxy.db.models import Proxy
from modules.proxy.db.schemas import ProxyRead, ProxyUpdate, ProxyCreate, ProxyCheck, ProxyCheckURL, ProxyReadSingle
from modules.proxy.dependencies.path import get_proxy_by_id
from modules.proxy.util.util import check_proxy_id_by_ipify, check_proxy_address_by_ipify, change_proxy_ip, restore_last_ip_from_redis

router = APIRouter(
    prefix='/proxies',
    dependencies=[Security(get_current_active_user, scopes=['proxy:sudo', 'proxy:proxies'])]
)


@router.get('/', response_model=list[ProxyRead])
async def get_proxy_list(request: Request, pagination: PaginationDep):
    query = await crud.proxy.query_get_multi(**pagination)
    proxies = await ProxyRead.from_queryset(query)

    await restore_last_ip_from_redis(proxies, request.app.redis)

    return proxies


@router.post('/check', response_model=ProxyCheck)
async def check_proxy(request: Request, proxy_data: ProxyCheckURL):
    result = None

    if proxy_data.proxy_address:
        result = await check_proxy_address_by_ipify(proxy_data.proxy_address)
    elif proxy_data.id:
        proxy = await crud.proxy.get(id=proxy_data.id)
        result = await check_proxy_id_by_ipify(proxy, request.app.redis)

    return JSONResponse(content=result)


@router.post('/change-status/{proxy_id}', response_model=ProxyReadSingle)
async def change_status(proxy: Proxy = Depends(get_proxy_by_id)):
    proxy.is_enabled = not proxy.is_enabled
    await proxy.save()
    return await ProxyReadSingle.from_tortoise_orm(proxy)


@router.post('/change-ip/{proxy_id}', response_model=ProxyCheck)
async def change_proxy(request: Request, proxy: Proxy = Depends(get_proxy_by_id)):
    result = await change_proxy_ip(proxy, request.app.redis)
    return JSONResponse(content=result)


@router.post('/', response_model=ProxyRead)
async def create_proxy(create_data: ProxyCreate):
    proxy = await crud.proxy.create(create_data)
    return await ProxyRead.from_tortoise_orm(proxy)


@router.get('/{proxy_id}', response_model=ProxyReadSingle)
async def get_proxy(proxy: Proxy = Depends(get_proxy_by_id)):
    return await ProxyReadSingle.from_tortoise_orm(proxy)


@router.put('/{proxy_id}', response_model=ProxyRead)
async def update_proxy(update_data: ProxyUpdate, proxy: Proxy = Depends(get_proxy_by_id)):
    proxy = await crud.proxy.update(proxy, update_data)
    return await ProxyRead.from_tortoise_orm(proxy)


@router.delete('/{proxy_id}')
async def del_proxy(proxy: Proxy = Depends(get_proxy_by_id)):
    await crud.proxy.remove(id=proxy.id)
    return Response(status_code=204)