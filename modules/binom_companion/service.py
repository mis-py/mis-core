import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import time
import ssl
import aiodns
import aiohttp
import urllib3
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
import asyncio
from aiohttp import ClientHttpProxyError
from fastapi_pagination.bases import AbstractParams
from loguru import logger
from tortoise.expressions import Subquery

from core.exceptions import NotFound, ValidationFailed
from core.utils.module.shared_hub import SharedHub
from core.utils.notification.eventory import eventory_publish
from core.utils.schema import PageResponse
from core.services.base.base_service import BaseService
from core.utils.common import exclude_none_values

from core.utils.app_context import AppContext
from .exceptions import ProxyDomainCheckError, NoProxiesError

from .schemas.lead_record import LeadRecordIn
from .repository import (
    TrackerInstanceRepository,
    ReplacementGroupRepository,
    ProxyDomainRepository,
    ReplacementHistoryRepository,
    LeadRecordRepository
)
from .db.models import (
    TrackerInstance,
    ReplacementGroup,
    ProxyDomain,
    ReplacementHistory,
    LeadRecord
)
from .schemas.proxy_domain import ProxyDomainCreateBulkModel
from .services.tracker import get_tracker_service
from .util.util import regexp_match, check_ssl_domain, SSLResponse


class ReplacementGroupService(BaseService):
    def __init__(self):
        super().__init__(repo=ReplacementGroupRepository(model=ReplacementGroup))

    async def get_groups_from_id(self, replacement_group_ids: list[int], is_active: bool = True) -> list[ReplacementGroup]:
        groups: list[ReplacementGroup] = await self.repo.filter(
            id__in=replacement_group_ids,
            prefetch_related=['tracker_instance']
        )

        not_exist_groups = list(
            set.symmetric_difference(
                set([str(group) for group in replacement_group_ids]),
                set([str(group.pk) for group in groups])
            )
        )

        if len(not_exist_groups) > 0:
            logger.warning(f"In requested group ids: {replacement_group_ids} "
                           f"next group ids: {not_exist_groups} is not exists and would not be used")

        not_active_groups = [group.pk for group in groups if not (group.is_active == is_active)]

        if len(not_active_groups) > 0:
            logger.warning(f"In requested group ids: {replacement_group_ids} "
                           f"next group ids: {not_active_groups} is not active and would not be used")

        active_groups = [group for group in groups if (group.is_active == is_active)]

        return active_groups

    async def proxy_change(self, ctx: AppContext, replacement_group_ids: list[int], reason: str):
        """ Function to run domain replacement for specific replacement groups with group validation """
        active_groups = await self.get_groups_from_id(replacement_group_ids=replacement_group_ids)

        if len(active_groups) > 0:
            return await ProxyDomainService().change_domain(ctx, active_groups, reason)
        else:
            logger.warning(f"Run replacement_group_proxy_change task ERROR: Nothing to run")

    async def fake_proxy_change(
            self,
            ctx: AppContext,
            replacement_group_ids: list[int],
            reason: str,
            domains: list[str],
            servers: list[str],
    ):
        """Function for adding replacement history without changing domains"""
        active_groups = await self.get_groups_from_id(replacement_group_ids=replacement_group_ids)

        if len(active_groups) == 0:
            raise ValidationFailed(f"No active replacement groups")

        if domains:
            proxy_domains = await ProxyDomainService().filter(name__in=domains)
        elif servers:
            proxy_domains = await ProxyDomainService().filter(server_name__in=servers)
        else:
            raise ValidationFailed(f"'domains' and 'servers' is empty")

        return await ProxyDomainService().fake_change_domain(
            ctx=ctx,
            groups=active_groups,
            reason=reason,
            domains=proxy_domains,
        )

    async def check_replacement_group(self, replacement_group_id: int):
        replacement_group: ReplacementGroup = await self.get(id=replacement_group_id,
                                                             prefetch_related=['tracker_instance'])
        tracker_service = get_tracker_service(replacement_group.tracker_instance.tracker_type)
        offer_ids, _ = await tracker_service.fetch_offers(
            replacement_group,
            replacement_group.tracker_instance
        )

        landing_ids, _ = await tracker_service.fetch_landings(
            replacement_group,
            replacement_group.tracker_instance
        )

        return {
            "offers": offer_ids,
            "landing": landing_ids
        }

    async def filter_with_history_and_paginate(
            self,
            history_limit: int,
            params: AbstractParams = None,
            **filters,
    ):
        filters_without_none = exclude_none_values(filters)
        queryset = await self.repo.filter_queryable_with_history(**filters_without_none)
        results = await self.repo.paginate(queryset=queryset, params=params)
        for item in results.result.items:
            item.replacement_history = item.replacement_history[:history_limit]
        return results

    async def get_with_history(self, history_limit: int, id: int, **filters):
        filters_without_none = exclude_none_values(filters)
        return await self.repo.get_with_history(
            replacement_group_id=id,
            history_limit=history_limit, **filters_without_none
        )

    async def check_group_domains(self, replacement_group_ids: list[int], proxy_ids: list[int]):
        proxy_service: 'ProxyService' = await SharedHub.execute(module='proxy_registry', func_key='get_proxy_service')
        proxies = await proxy_service.filter_by_ids(proxy_ids)
        proxies_address = [proxy.address for proxy in proxies]

        proxy_checker: 'ProxyChecker' = await SharedHub.execute(module='proxy_registry', func_key='get_proxy_checker')
        valid_proxies = await proxy_checker.filter_valid_proxies(proxies_address)

        if not valid_proxies:
            raise NoProxiesError("No valid proxies for check domains!")

        replacement_groups: list[ReplacementGroup] = await self.repo.filter(
            id__in=replacement_group_ids,
            prefetch_related=['tracker_instance']
        )

        return await self.fetch_and_check_group_domains(
            replacement_groups=replacement_groups,
            proxies=valid_proxies,
        )

    async def fetch_and_check_group_domains(
            self,
            replacement_groups: list[ReplacementGroup],
            proxies: list[str],
    ) -> list:
        result = []

        for group in replacement_groups:
            replacement_group_result = {
                'replacement_group_id': group.pk,
                'domains': [],
            }

            tracker_service = get_tracker_service(group.tracker_instance.tracker_type)
            _, offer_domains = await tracker_service.fetch_offers(group=group, instance=group.tracker_instance)
            _, landing_domains = await tracker_service.fetch_landings(group=group, instance=group.tracker_instance)

            domains = set(offer_domains + landing_domains)
            for domain in domains:
                try:
                    await self.check_domain_by_proxies(domain=domain, proxies=proxies)
                    replacement_group_result['domains'].append({'name': domain, 'status': True, 'message': 'ok'})
                except ProxyDomainCheckError as error:
                    replacement_group_result['domains'].append({'name': domain, 'status': False, 'message': str(error)})
                    logger.warning(f"[{domain}] {str(error)}")

            result.append(replacement_group_result)

        return result

    async def check_domain_by_proxies(self, domain: str, proxies: list[str]):
        for proxy in proxies:
            connector = ProxyConnector.from_url(proxy)
            async with aiohttp.ClientSession(connector=connector) as session:
                try:
                    async with session.get(f'https://{domain}') as response:

                        if response.status != 200:
                            raise ProxyDomainCheckError(f"GET status: {response.status}")

                        text = await response.text()
                        if text != 'ok':
                            raise ProxyDomainCheckError(f"Response content not 'ok'! Content: {text}")

                except Exception as e:
                    raise ProxyDomainCheckError(f"Request error: {e.__class__.__name__} {e}")

        logger.success(f"[{domain}] checks passed")


class ProxyDomainService(BaseService):
    def __init__(self):
        super().__init__(repo=ProxyDomainRepository(model=ProxyDomain))
        self.history = ReplacementHistoryRepository(model=ReplacementHistory)
        self.tracker_instance_repo = TrackerInstanceRepository(model=TrackerInstance)

    async def get_history_domains(
            self,
            prefetch_related: list[str] = None,
            params: AbstractParams = None,
            **filters
    ) -> PageResponse:
        queryset = await self.history.filter_queryable(prefetch_related, **filters)
        return await self.history.paginate(queryset=queryset, params=params)

    async def get_new_domains(self, group: ReplacementGroup):
        """
        Use this function to get only working and ready domains for replacement group!
        :param group:
        :return:
        """
        # get all domains for specific group
        subfilter = await self.history.filter_queryable(replacement_group_id=group.pk)
        subfilter_values = subfilter.values('to_domain_id')

        # get domains except id that was used and is not invalid
        query = await self.repo.filter_queryable(
            id__not_in=Subquery(subfilter_values),
            is_invalid=False,
            is_ready=True,
            tracker_instances=group.tracker_instance.pk,
            prefetch_related=["tracker_instances"]
        )

        result = await query

        return result

    async def get_new_domains_for_selected_groups(self, groups: list[ReplacementGroup]) -> list[ProxyDomain]:
        """
        Use this function if you need to get new ready and working domains for specified replacement groups!
        :param groups:
        :return:
        """
        # For every group we get available domains that was not used previously
        available_domains_for_group: dict[str, ProxyDomain] = {}
        for group in groups:
            available_domains_for_group[group.name] = await self.get_new_domains(group=group)

        filtered_items = [item for item in available_domains_for_group.values() if item]

        return filtered_items

    async def find_intersection(self, groups: list[ReplacementGroup]) -> set:
        """Use this function if you need to find only domains available for all groups!"""
        group_items = await self.get_new_domains_for_selected_groups(groups)

        # In available domains find domain that available for all groups else return emty set
        intersection = set.intersection(*[set(item) for item in group_items if item]) if group_items else set()

        return intersection

    async def get_new_domain_for_selected_groups(self, groups: list[ReplacementGroup]) -> ProxyDomain:
        """Use this function if you need to get single ready and working domain for specified groups"""
        group_ids = [group.pk for group in groups]

        intersection = await self.find_intersection(groups)

        if not intersection:
            raise NotFound(f"Not found available domains for groups: {group_ids}")

        # logger.debug(intersection)
        class Proxy:
            name: str = 'without'

        proxy = Proxy()

        new_domain = None

        for domain in intersection:
            domain_valid = await self.is_domain_ok_by_proxy(domain.name, proxy)

            if not domain_valid:
                # logger.warning(f'[{geo.name}] Skip {row_domain.domain} - due to proxy not work!')
                # skip this proxy in case of it's down or broken
                # TODO mark domain is invalid
                await self.set_is_invalid(domain.pk)
                continue

            new_domain = domain
            break

        # new_domain = intersection.pop()

        # logger.debug(new_domain)

        if not new_domain:
            raise NotFound(f"Not found new domain for groups: {group_ids}")

        return new_domain

    async def is_change_domain_cooldown_pass(self, replacement_group_id: int, cooldown: int):
        """
        Search for last used domain in specific replacement group and compare with cooldown value.
        Useful for automatic change with certain cooldown

        :param replacement_group_id:
        :param cooldown:
        :return:
        """
        now = datetime.now(timezone.utc)
        query = await self.history.filter_queryable(replacement_group_id=replacement_group_id)
        last_changed_domain = await query.order_by('-date_changed').first()

        if last_changed_domain and last_changed_domain.date_changed > now - timedelta(seconds=cooldown):
            return False
        return True

    async def change_domain(self, ctx: AppContext, groups: list[ReplacementGroup], reason: str) -> dict:
        """
        Function to changing offers/landings domain. It does not perform any group validations!
        :param ctx:
        :param groups:
        :return:
        """
        group_ids = [group.pk for group in groups]
        logger.debug(f"Run change_domain task for group: {group_ids}")

        new_domain = await self.get_new_domain_for_selected_groups(groups)

        change_result = {}

        for group in groups:
            instance = group.tracker_instance
            tracker_service = get_tracker_service(instance.tracker_type)

            offers, old_offers_domains = await tracker_service.fetch_offers(group=group, instance=instance)
            landings, old_land_domains = await tracker_service.fetch_landings(group=group, instance=instance)

            offer_response = await tracker_service.change_offers_domain(offers, new_domain, instance=instance)
            logger.debug(
                f'Group: {group}, new domain: {new_domain}, offers: {offers}, result: {offer_response if len(offer_response) > 0 else "No offers to change"}'
            )

            landing_response = await tracker_service.change_landings_domain(
                landings, new_domain, instance=instance
            )
            logger.debug(
                f'Group: {group}, new domain: {new_domain}, landings: {landings}, result: {landing_response if len(landing_response) > 0 else "No landings to change"}'
            )

            if len(offer_response) or len(landing_response):
                # make history record and eventory publish only if we actually changed something
                await eventory_publish(
                    body={
                        'group_name': group.name,
                        'new_domain': new_domain.name,
                        'old_domains': old_offers_domains + old_land_domains
                    },
                    routing_key=ctx.routing_keys.DOMAIN_CHANGED,
                    channel_name=ctx.app_name,
                )

                await self.add_history_record(
                    new_domain=new_domain,
                    previous_domains=old_offers_domains + old_land_domains,
                    offers_list=offers,
                    lands_list=landings,
                    replaced_by=ctx.user,
                    replacement_group=group,
                    reason=reason
                )

            change_result["new_domain"] = new_domain.name

            change_result["replacement_groups"] = list()

            group_result = dict(
                id=group.pk,
                name=group.name,
                offer_ids=offers,
                offer_result=offer_response,
                landing_ids=landings,
                landing_result=landing_response
            )

            change_result["replacement_groups"].append(group_result)

        return change_result

    async def fake_change_domain(
            self,
            ctx: AppContext,
            groups: list[ReplacementGroup],
            reason: str,
            domains: list[ProxyDomain],
    ):
        """
        Function to adding replacement history without changing domains on tracker
        """

        group_ids = [group.pk for group in groups]
        logger.debug(f"Run fake_change_domain task for group: {group_ids}")
        for group in groups:
            instance = group.tracker_instance
            tracker_service = get_tracker_service(instance.tracker_type)

            offers, old_offers_domains = await tracker_service.fetch_offers(group=group, instance=instance)
            landings, old_land_domains = await tracker_service.fetch_landings(group=group, instance=instance)

            for new_domain in domains:
                await self.add_history_record(
                    new_domain=new_domain,
                    previous_domains=old_offers_domains + old_land_domains,
                    offers_list=offers,
                    lands_list=landings,
                    replaced_by=ctx.user,
                    replacement_group=group,
                    reason=reason
                )

    async def add_history_record(
            self,
            new_domain: ProxyDomain,
            previous_domains: list[ProxyDomain],
            offers_list: list[str],
            lands_list: list[str],
            replaced_by: 'User',
            replacement_group: ReplacementGroup,
            reason: str
    ):
        previous_domains_models: list[ProxyDomain] = await self.repo.filter(
            name__in=previous_domains
        )

        new_record: ReplacementHistory = await self.history.create(data=dict(
            offers=offers_list,
            lands=lands_list,
            replaced_by=replaced_by,
            to_domain=new_domain,
            replacement_group=replacement_group,
            reason=reason
        ))

        await new_record.from_domains.add(*previous_domains_models)

    async def create_bulk(self, proxy_domains_in: ProxyDomainCreateBulkModel, ctx: AppContext) -> list[ProxyDomain]:
        created_domains = []
        for domain in proxy_domains_in.domain_names:
            try:
                created_domain = await self.create_by_kwargs(
                    name=domain,
                    server_name=proxy_domains_in.server_name
                )
                await self.set_trackers(created_domain, tracker_instance_ids=proxy_domains_in.tracker_instance_ids)
                await created_domain.fetch_related("tracker_instance")

                await eventory_publish(
                    body={"id": created_domain.pk, "name": created_domain.name},
                    routing_key=ctx.routing_keys.PROXY_DOMAIN_ADDED,
                    channel_name=ctx.app_name,
                )

            except Exception as e:
                # TODO notify in response if skipped some domains
                logger.warning(f"Skipped creating domain: {domain}, exception: {e}")
                continue

        return created_domains

    async def update_bulk(self, schema_in):
        proxy_domains = await self.repo.update_bulk(
            data_items=schema_in.model_dump(exclude_unset=True)['proxy_domains'],
            update_fields=['name', 'server_name', 'is_invalid', 'is_ready'],
        )

        # update trackers
        schema_proxy_domains_dict = {schema_domain.id: schema_domain for schema_domain in schema_in.proxy_domains}
        for proxy_domain in proxy_domains:
            schema_proxy_domain = schema_proxy_domains_dict.get(proxy_domain.pk)
            if schema_proxy_domain and schema_proxy_domain.tracker_instance_ids:
                await self.clear_trackers(proxy_domain)
                await self.set_trackers(proxy_domain, schema_proxy_domain.tracker_instance_ids)

    async def get_server_names(self):
        base_query = await self.repo.filter_queryable()
        result = base_query.order_by("server_name").distinct().values_list('server_name', flat=True)
        return dict(server_names=await result)

    async def set_is_valid(self, domain_id: int):
        return await self.repo.update(id=domain_id, data={'is_invalid': False})

    async def set_is_invalid(self, domain_id: int):
        return await self.repo.update(id=domain_id, data={'is_invalid': True})

    async def check_domain_with_proxy(self, domain, proxy_url=None, retries=3):
        # proxy_connector = ProxyConnector.from_url(proxy_url)

        async with ClientSession(response_class=SSLResponse) as session:  # connector=proxy_connector,
            last_exception = None
            for retry in range(0, retries):
                try:
                    async with session.get(f'https://{domain}/', timeout=5) as response:
                        if not check_ssl_domain(response.certificate):
                            # TODO check with expired cert
                            return ssl.SSLCertVerificationError(f"{domain} - {response.certificate}")

                        response_text = await response.text()

                        if response_text != 'ok':
                            return ValueError(f"{domain} - {response_text}")

                        return None

                except ssl.SSLError as e:
                    return ssl.SSLError(f"{domain} - {e}")

                except Exception as e:
                    await asyncio.sleep(5)
                    last_exception = e

        return last_exception

    # TODO recreate it to aiohttp with concurrency in case of long check time (function exists in utils)
    async def is_domain_ok_by_proxy(self, domain: str, proxy) -> bool | None:
        start_time = time.time()
        response = await self.check_domain_with_proxy(domain)  # , proxy.address)

        if isinstance(response, ssl.SSLCertVerificationError):
            logger.warning(f'[{domain}] {proxy.name}: Possible expired certificate {response}')
            return False

        if isinstance(response, ssl.SSLError):
            logger.warning(f'[{domain}] {proxy.name}: Invalid SSL certificate {response}')
            return False

        elif isinstance(response, ValueError):
            logger.warning(f'[{domain}] {proxy.name}: Response is not "ok" {response}')
            return False

        elif isinstance(response, ClientHttpProxyError):
            logger.warning(f'[{domain}] {proxy.name}: ({response.__class__.__name__}) {response}')
            return False

        elif isinstance(response, ConnectionResetError):
            logger.warning(
                f'[{domain}] {proxy.name}: ({response.__class__.__name__}) {response} Possible block, check it manually')
            return False

        # commented coz work not as expected
        # returns 502 instead or tunnel error
        # elif isinstance(response, ProxyError):
        #     logger.warning(f'[{domain}] {proxy.name}: Proxy is possible down or inaccessible {response}')
        #     # return None because it is out of context domain validation, it is proxy down or broken
        #     return None

        elif isinstance(response, Exception):
            logger.warning(f'[{domain}] {proxy.name}: ({response.__class__.__name__}) {response}')
            return False

        logger.info(f'[{domain}]: Proxy check passed! Verify took {round(time.time() - start_time, 2)}s')

        return True

    # async def check_domain_valid(self, domain_id: int) -> ProxyDomain:
    #     domain = await self.get(id=domain_id, prefetch_related=['tracker_instance'])
    #     class Proxy:
    #         name: str = 'without'
    #
    #     proxy = Proxy()
    #
    #     await self.is_domain_ok_by_proxy(domain.name, proxy)
    #     return domain

    async def set_trackers(self, proxy_domain: ProxyDomain, tracker_instance_ids: list[int]):
        tracker_instances = await self.tracker_instance_repo.filter(id__in=tracker_instance_ids)
        await proxy_domain.tracker_instances.add(*tracker_instances)

    async def clear_trackers(self, proxy_domain: ProxyDomain):
        await proxy_domain.tracker_instances.clear()


class LeadRecordService(BaseService):
    def __init__(self):
        super().__init__(repo=LeadRecordRepository(model=LeadRecord))

    async def add_new_record(self, ctx: AppContext, new_lead: LeadRecordIn):
        # if new_lead.id is None:
        #     return Response(status_code=400)

        # logger.debug(new_lead)

        # if not new_lead.us:  # skipping lead without tag
        #     logger.warning('Got lead without tag!')
        #     logger.warning(f' - new_lead.alter_id = {new_lead.id}')
        #     logger.warning(f' - {new_lead.country = }')
        #     logger.warning(f' - {new_lead.offer_id = }')
        #     logger.warning(f' - {new_lead.landing = }')
        #     return Response(status_code=200)

        if new_lead.us is not None and re.match('aff[0-9]+-[0-9]+', new_lead.us):
            new_lead.us, new_lead.landing = new_lead.us.split('-')

        # Android app campaign naming
        if new_lead.us is not None and re.match('^[A-Z]+_[A-Za-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9]+$', new_lead.us):
            new_lead.us, _, _, _ = new_lead.us.split('_')

        # Android app campaign naming
        if new_lead.us is not None and len(new_lead.us) > 10:
            new_lead.us = new_lead.us[:2]

        if not new_lead.us:
            logger.debug(f"Possible wrong utm source: {new_lead}")
            new_lead.us = ""

        url = urllib3.util.parse_url(new_lead.referer or new_lead.origin)
        new_lead.origin = url.host
        new_lead.referer = url.host

        # await self.create(
        #     new_lead
        # )
        #
        # await Eventory.publish(
        #     obj=Message(
        #         source_type=Message.Source.EXTRA,
        #         data_type=Message.Data.INFO,
        #         recipient=Recipient(user_id=1),
        #         body=new_lead.dict(),
        #     ),
        #     routing_key=ctx.routing_keys.NEW_LEAD,
        #     app_name=ctx.app_name
        # )

    async def check_lead_rate(self, geo: str, last_period: int, previous_period: int, diff_percent: float) -> bool:
        now = datetime.now(timezone.utc)

        last_period_leads = (await self.repo.filter(
            time__gte=now - timedelta(seconds=last_period),
            geo=geo,
        )).count()

        previous_period_leads = (await self.repo.filter(
            geo=geo,
            time__gte=now - timedelta(seconds=last_period + previous_period),
            time__lte=now - timedelta(seconds=last_period)
        )).count()

        if previous_period_leads == 0 and last_period_leads == 0:
            logger.debug(f'[{geo}] prev {previous_period_leads} == last {last_period_leads}, skip')
            return False

        if previous_period_leads == 0:
            logger.debug(f'[{geo}] prev {previous_period_leads}, last {last_period_leads}, skip')
            return False

        def get_lead_diff_change(last, previous):
            if last == previous:
                return 0
            try:
                return 100 - ((last / previous) * 100.0)
            except ZeroDivisionError:
                return 0

        diff = get_lead_diff_change(last_period_leads, previous_period_leads)

        if diff >= diff_percent:
            logger.debug(f'[{geo}] Diff {diff:.1f}% between previous: {previous_period_leads} '
                         f'and last: {last_period_leads} periods, our level is: {diff_percent}%')
            return True
        return False

    async def check_last_lead_time_by_geo(self, geo, max_time_since_last_lead):
        now = datetime.now(timezone.utc)

        last_geo_lead = (await self.repo.filter_queryable(
            geo=geo.name,
        )).order_by('-time').first()

        if not last_geo_lead:
            logger.debug(f"[{geo.name}] No leads registered in DB for specified GEO.")
            return False

        time_since_last_lead = int((now - last_geo_lead.time).total_seconds())

        if time_since_last_lead >= max_time_since_last_lead:
            logger.debug(
                f"[{geo.name}] Time since last lead: {time_since_last_lead} exceed maximum: {max_time_since_last_lead}"
            )

        return time_since_last_lead

    async def check_last_lead_time_by_user_tag(self, user_tag: str, max_time_since_last_lead):
        now = datetime.now(timezone.utc)

        last_geo_lead = (await self.repo.filter(
            tag=user_tag,
        )).order_by('-time').first()

        if not last_geo_lead:
            logger.debug(f"[{user_tag}] No leads registered in DB for specified GEO.")
            return False

        # logging.debug(last_geo_lead)

        time_since_last_lead = int((now - last_geo_lead.time).total_seconds())

        if time_since_last_lead >= max_time_since_last_lead:
            logger.debug(
                f"[{user_tag}] Time since last lead: {time_since_last_lead} exceed maximum: {max_time_since_last_lead}"
            )

        return time_since_last_lead


class YandexBrowserCheckService:

    async def check_domains(self, domains: list[str], yandex_api_key: str) -> list[str]:
        """Return malware domains if found"""
        if not domains:
            return []

        url_with_key = f"https://sba.yandex.net/v4/threatMatches:find?key={yandex_api_key}"

        payload = {
            "client": {
                "clientId": "your_client_name",
                "clientVersion": "1.0"
            },
            "threatInfo": {
                "threatTypes": [
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                    "THREAT_TYPE_UNSPECIFIED",
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                ],
                "platformTypes": ["WINDOWS", "CHROME", "ANDROID", "IOS"],
                "threatEntryTypes": ["URL"],
                "threatEntries": self.make_threat_entries(domains)
            }
        }
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url_with_key, data=json.dumps(payload), headers=headers) as response:
                response_data = await response.json()

        banned_domains = self.banned_domains_from_response(response_data)
        return banned_domains

    def banned_domains_from_response(self, data: dict) -> list:
        banned_domains = []
        if 'matches' not in data:
            return banned_domains

        for match in data['matches']:
            domain = self.extract_domain(match['threat']['url'])
            banned_domains.append(domain)
        return list(set(banned_domains))

    def make_threat_entries(self, domains: list[str]):
        entries = []
        for domain in domains:
            entries.append({
                'url': f"https://{domain}"
            })
        return entries

    def extract_domain(self, url: str):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain


class DNSCheckerService:

    async def check_record(self, domain: str, record: str = 'A'):
        resolver = aiodns.DNSResolver()
        try:
            await resolver.query(domain, record)
            return True
        except aiodns.error.DNSError:
            return False
