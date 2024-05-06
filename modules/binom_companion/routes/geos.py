from fastapi import APIRouter, Response, Security, Depends

from core.dependencies.path import PaginationDep
from core.dependencies.security import get_current_user
from ..db import crud
from ..db.models import BinomGeo
from ..db.schemas import GeoCreateModel, GeoOutModel, GeoUpdateModel
from ..dependencies.path import get_geo_by_id


router = APIRouter(
    dependencies=[Security(get_current_user, scopes=['binom_companion:sudo', 'binom_companion:geos'])]
)


@router.get('/geo/{geo_id}', response_model=GeoOutModel)
async def get_geo_endpoint(geo: BinomGeo = Depends(get_geo_by_id)):
    return await GeoOutModel.from_tortoise_orm(geo)


@router.get('/geo', response_model=list[GeoOutModel])
async def get_geos_endpoint(pagination: PaginationDep):
    return await GeoOutModel.from_queryset(await crud.geo.query_get_multi(**pagination))


@router.post('/geo', response_model=GeoOutModel)
async def add_geo_endpoint(geo_model: GeoCreateModel, current_user=Depends(get_current_user)):
    geo = await crud.geo.create_with_owner(geo_model, user_id=current_user.id)
    return await GeoOutModel.from_tortoise_orm(geo)


@router.put('/geo/{geo_id}', response_model=GeoOutModel)
async def update_geo_endpoint(geo_model: GeoUpdateModel, geo: BinomGeo = Depends(get_geo_by_id)):
    await crud.geo.update(geo, geo_model)
    return await GeoOutModel.from_tortoise_orm(geo)


@router.delete('/geo/{geo_id}')
async def delete_geo_endpoint(geo: BinomGeo = Depends(get_geo_by_id)):
    await crud.geo.remove(id=geo.id)
    return Response(status_code=204)
