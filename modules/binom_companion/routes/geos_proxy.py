from fastapi import APIRouter, Security

from core.dependencies.security import get_current_user
# from modules.proxy.db.schemas import ProxyRead, ProxyCreateOutside
# from modules.proxy.services import create_proxy, get_proxy, remove_proxy

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=['binom_companion:sudo', 'binom_companion:geos'])]
)


# @router.post('/proxy/{geo_id}/', response_model=ProxyRead)
# async def add_geo_proxy_endpoint(proxy_model: ProxyCreateOutside, geo: Geo = Depends(get_geo_by_id)):
#     proxy = await create_proxy(
#         address=proxy_model.address,
#         change_url=proxy_model.change_url,
#         name=proxy_model.name,
#         instance=geo,
#         is_multi=True,
#     )
#     return ProxyRead.from_orm(proxy)
#
#
# @router.get('/proxy/{geo_id}/', response_model=list[ProxyRead])
# async def get_proxy_endpoint(geo: Geo = Depends(get_geo_by_id)):
#     return await get_proxy(geo, is_multi=True)
#
#
# @router.delete('/proxy/{geo_id}/{proxy_id}')
# async def del_geo_proxy_endpoint(proxy_id: int, geo: Geo = Depends(get_geo_by_id)):
#     await remove_proxy(geo, proxy_id)
#     return Response(status_code=204)
