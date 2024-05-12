# from loguru import logger
# from tortoise.transactions import in_transaction

# from services.variables.variable_set import VariableSet
# from ..db.dataclass import DomainStatus
# from ..exceptions import ChangeDomainError
# from ..util import is_domain_ok_by_proxy
# from ..util.offers import change_offers_domain, get_offers
# from ..util.util import clamp
# from modules.core.dependencies import SettingsProxy
# from modules.proxy.services import get_proxy

# from services.redis import RedisService


# async def add_geo_in_banned(domain: Domain) -> Domain:
#     await domain.banned_geo.add(await domain.current_geo)
#     return domain


# async def set_domain_as_active(domain: Domain, geo: BinomGeo) -> Domain:
#     domain.status = DomainStatus.ACTIVE
#     domain.current_geo = geo
#     await domain.save()
#     return domain


# async def set_status_not_work(domain: Domain) -> Domain:
#     domain.status = DomainStatus.NOT_WORK
#     await domain.save()
#     return domain


# async def update_domain_status(domain: Domain):
#     allowed_geos = await domain.allowed_geo.all().values_list('id', flat=True)
#     banned_geos = await domain.banned_geo.all().values_list('id', flat=True)
#
#     allowed_geos.sort()
#     banned_geos.sort()
#     if allowed_geos == banned_geos:
#         domain.status = DomainStatus.USED
#     else:
#         domain.status = DomainStatus.REUSE
#     domain.current_geo = None
#     await domain.save()


# async def get_current_domain(geo_id: int) -> Domain:
#     return await Domain.filter(current_geo=geo_id, status=DomainStatus.ACTIVE).first()


# async def get_all_geos() -> list[BinomGeo]:
#     return await BinomGeo.all()


# async def set_new_domain_for_offers(domain: str, geo_name: str, variables: VariableSet):
#     offers, domains = await get_offers(geo_name=geo_name, variables=variables)
#     await change_offers_domain(offers, domain, variables)
#     logger.warning(f'Domain changed, new domain is: {domain}')
#     logger.warning(f'Old domains was: {domains}')
#
#     await ChangedDomain.create(
#         from_domains=",".join(domains),
#         to_domain=domain,
#         geo=geo_name,
#         offers=offers
#     )

# that was writed for endpoint manual change
# async def change_domain(geo_id, variables: VariableSet) -> Domain:
#     async with in_transaction():
#         new_domain = await get_available_domain(geo_id=geo_id)
#         if not new_domain:
#             raise ChangeDomainError('No domains available')
#
#         previous_domain = await get_current_domain(geo_id=geo_id)
#         if previous_domain:
#             await add_geo_in_banned(previous_domain)
#             await update_domain_status(previous_domain)
#
#         geo = await BinomGeo.get(id=geo_id)
#
#         # proxies = await get_proxy(geo, is_multi=True)
#         # for proxy in proxies:
#         #     if not await is_domain_ok_by_proxy(new_domain.domain, proxy):
#         #         await set_status_not_work(new_domain)
#         #         logger.error(f'Domain {new_domain.domain} is not responding "ok"')
#         #         raise ChangeDomainError(f'Domain {new_domain.domain} failed proxy check')
#
#         await set_domain_as_active(domain=new_domain, geo=geo)
#         await set_new_domain_for_offers(domain=new_domain.domain, geo=geo.name, variables=variables)
#     return new_domain


# async def get_available_geos(user_id: int) -> list[BinomGeo]:
#     return await BinomGeo.filter(is_check=True, user_id=user_id)


# async def _scan_task_keys(geo: BinomGeo):
#     cursor, keys = await RedisService.scan(match=f'task_value:{geo.name}={geo.pk}:*')
#     return cursor, keys
#
#
# async def get_task_values(geo: BinomGeo):
#     cursor, keys = await _scan_task_keys(geo)
#
#     values = await RedisService.mget(keys)
#
#     return values
#
#
# # Clear all values if task not specified or clear only task values if specified
# async def clear_task_value(geo: BinomGeo):
#     cursor, keys = await _scan_task_keys(geo)
#
#     await RedisService.client.delete(*keys)
#
#
# async def increase_task_value(
#     geo: BinomGeo,
#     task_name: str,
#     value: float
# ):
#     # cast to float due to setting is string actually
#     value = float(value)
#
#     # get key value or if None take initial value 0.0
#     prev_value = await RedisService.cache.get_json(
#         cache_name="task_value",
#         key=f"{geo.name}={geo.pk}:{task_name}",
#     ) or 0.0
#
#     new_value = clamp(prev_value + value, 0.0, 2.0)
#
#     await RedisService.cache.set(
#         cache_name=f"task_value",
#         key=f"{geo.name}={geo.pk}:{task_name}",
#         value=new_value,
#         # time=timedelta(minutes=5)
#     )
#
#     if prev_value != new_value:
#         logger.debug(f"[{geo.name}] Task: {task_name}, value: {value}, change: {prev_value} -> {new_value}")
#
#     # await geo.save()
#
#
# async def decrease_task_value(
#     geo: BinomGeo,
#     task_name: str,
#     value: float
# ):
#     # cast to float due to setting is string actually
#     value = float(value)
#
#     return await increase_task_value(geo, task_name, value * (-1.0))
#
#
# async def get_task_keys_and_values(geo: BinomGeo):
#     cursor, keys = await _scan_task_keys(geo)
#     values = await RedisService.mget(keys)  # values ordered identically to keys
#     return keys, values
#
#
# async def get_geo_task_checks_result(geo: BinomGeo):
#     keys, values = await get_task_keys_and_values(geo)
#
#     result = {}
#     for key, value in zip(keys, values):
#         result[key.rsplit(":", 1)[1]] = float(value)
#     return result
