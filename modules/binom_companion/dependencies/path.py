from fastapi.params import Path, Query
from core.exceptions.exceptions import NotFound

from .uow import UnitOfWorkDep
from ..service import DomainService, GeoService


async def get_domain_by_id(uow: UnitOfWorkDep, domain_id: int = Path()):
    domain = await DomainService(uow).get(id=domain_id)
    if not domain:
        raise NotFound("Domain not found")
    return domain


async def get_geo_by_id(uow: UnitOfWorkDep, geo_id: int = Path()):
    geo = await GeoService(uow).get(id=geo_id)
    if not geo:
        raise NotFound("Geo not found")
    return geo


async def get_geo_by_id_query(uow: UnitOfWorkDep, geo_id: int = Query()):
    geo = await GeoService(uow).get(id=geo_id)
    if not geo:
        raise NotFound("Geo not found")
    return geo
