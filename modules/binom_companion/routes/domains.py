from typing import Optional

from fastapi import APIRouter, Response, Security, Query, Depends, Request

from core.dependencies.security import get_current_user
from core.dependencies.path import PaginationDep
# from core.dependencies.variables import get_settings_proxy, SettingsProxy


from ..db import crud
from ..db.dataclass import DomainStatus
from ..db.models import Domain, BinomGeo
from ..db.schemas import (
    DomainCreateModel,
    DomainOutModel,
    DomainUpdateModel,
    DomainListCreateModel,
)
from ..dependencies.path import get_domain_by_id, get_geo_by_id_query
from ..util.redis_utils import change_domain, get_geo_task_checks_result

router = APIRouter(
    dependencies=[Security(get_current_user, scopes=['binom_companion:sudo', 'binom_companion:domains'])]
)


@router.get('/domain/{domain_id}', response_model=DomainOutModel)
async def get_domain_endpoint(domain: Domain = Depends(get_domain_by_id)):
    return await DomainOutModel.from_tortoise_orm(domain)


@router.get('/domain', response_model=list[DomainOutModel])
async def get_domains_endpoint(
        request: Request,
        pagination: PaginationDep,
        status: DomainStatus = None,
        in_use: Optional[bool] = None,
        current_geos: list[int] = Query(default=[]),
        allowed_geos: list[int] = Query(default=[]),
        banned_geos: list[int] = Query(default=[]),
):
    queryset = await crud.domain.query_filter_by_query_params(
        **pagination,
        status=status,
        in_use=in_use,
        current_geos=current_geos,
        allowed_geos=allowed_geos,
        banned_geos=banned_geos,
    )

    schema = await DomainOutModel.from_queryset(queryset)
    for domain in schema:
        if not domain.current_geo:
            continue

        # set task_check_statuses from redis cache
        domain.current_geo.task_check_statuses = await get_geo_task_checks_result(
            geo=domain.current_geo,
        )

    return schema


@router.post('/domain', response_model=DomainOutModel)
async def add_domain_endpoint(domain_model: DomainCreateModel):
    create_data = domain_model.dict()
    create_data.pop("allowed_geo", False)

    domain = await crud.domain.create_from_dict(create_data)
    allowed_geos = await crud.geo.filter_by_ids(ids=domain_model.allowed_geo)
    await crud.domain.set_allowed_geos(domain=domain, geos=allowed_geos)
    return await DomainOutModel.from_tortoise_orm(domain)


@router.post('/domain/bulk', response_model=list[DomainOutModel])
async def add_list_domain_endpoint(domain_model: DomainListCreateModel):
    allowed_geos = await crud.geo.filter_by_ids(ids=domain_model.allowed_geo)

    domain_for_output = []
    for domain in domain_model.domain:
        new_domain = await Domain.create(
            domain=domain,
            status=domain_model.status,
        )
        domain_for_output.append(new_domain)
        await crud.domain.set_allowed_geos(domain=domain, geos=allowed_geos)
    return domain_for_output


@router.put('/domain/{domain_id}', response_model=DomainOutModel)
async def update_domain_endpoint(domain_model: DomainUpdateModel, domain: Domain = Depends(get_domain_by_id)):
    await crud.domain.update(domain, domain_model)
    return await DomainOutModel.from_tortoise_orm(domain)


@router.put('/domain/{domain_id}/allowed_geo', response_model=DomainOutModel)
async def set_allowed_geo_for_domain_endpoint(allowed_geo_ids: list[int], domain: Domain = Depends(get_domain_by_id)):
    allowed_geos = await crud.geo.filter_by_ids(ids=allowed_geo_ids)
    await crud.domain.set_allowed_geos(domain=domain, geos=allowed_geos)
    return await DomainOutModel.from_tortoise_orm(domain)


@router.put('/domain/{domain_id}/banned_geo', response_model=DomainOutModel)
async def set_banned_geo_for_domain_endpoint(banned_geo_ids: list[int], domain: Domain = Depends(get_domain_by_id)):
    banned_geos = await crud.geo.filter_by_ids(ids=banned_geo_ids)
    await crud.domain.set_banned_geos(domain=domain, geos=banned_geos)
    return await DomainOutModel.from_tortoise_orm(domain)


@router.delete('/domain/{domain_id}')
async def delete_domain_endpoint(domain: Domain = Depends(get_domain_by_id)):
    await crud.domain.remove(id=domain.id)
    return Response(status_code=204)


# @router.get('/domain-change')
# async def change_domain_endpoint(
#         geo: Geo = Depends(get_geo_by_id_query),
#         settings: SettingsProxy = Depends(get_settings_proxy)):
#     domain = await change_domain(geo.id, variables=settings)
#     return await DomainOutModel.from_tortoise_orm(domain)


@router.get('/current-domain', response_model=DomainOutModel)
async def current_domain_endpoint(geo: BinomGeo = Depends(get_geo_by_id_query)):
    domain = await crud.domain.get_or_raise(current_geo_id=geo.id, status=DomainStatus.ACTIVE)
    return await DomainOutModel.from_tortoise_orm(domain)
