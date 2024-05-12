import re
from datetime import datetime, timedelta, timezone
import aiohttp
import urllib3
from fastapi_pagination.bases import AbstractParams
from loguru import logger
from ujson import loads, JSONDecodeError
from tortoise.expressions import Subquery

from core.exceptions import NotFound
from core.utils.notification.message import Message
from core.utils.notification.recipient import Recipient
from core.utils.schema import PageResponse
from core.services.base.base_service import BaseService

from libs.eventory import Eventory
from libs.modules.AppContext import AppContext

from .schemas.lead_record import LeadRecordModel
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
from .schemas.proxy_domain import ProxyDomainCreateModel
from .util.util import regexp_match


class TrackerInstanceService(BaseService):
    def __init__(self):
        super().__init__(repo=TrackerInstanceRepository(model=TrackerInstance))

    async def check_connection(self, tracker_instance_id: int):
        tracker_instance = await self.get(id=tracker_instance_id)

        json_data = await self.make_tracker_get_request(
            page='Offers',
            instance=tracker_instance
        )

        if json_data and len(json_data) > 0:
            return True
        return False

    @staticmethod
    async def make_tracker_get_request(
            instance: TrackerInstance,
            page: str,
            group: str = 'all',
            networks_filter: str = 'all'
    ):
        """
        Typical get request must return array with some objects
        """

        async with aiohttp.ClientSession() as session:
            url = f"{instance.base_url}/{instance.get_route}?page={page}&user_group=all" \
                  f"&status=1&group={group}&networks_filter={networks_filter}" \
                  f"&date=3&api_key={instance.api_key}"
            # logger.debug(url)
            response = await session.get(url)
            # logger.debug(await response.json(content_type='text/html'))
            if not response.ok:
                logger.error(f'Invalid response from Tracker {instance.name}: {response.status} {response.text}')
                return None

            try:
                data = await response.json(loads=loads, content_type=None)
            except JSONDecodeError:
                logger.error(f'Invalid data from Tracker {instance.name}: {response.text}')
                return None

            if not isinstance(data, list):
                logger.error(f'Got non-array data from Tracker {instance.name}: {data=}')
                return None

            return await response.json(content_type='text/html')

    @staticmethod
    async def make_tracker_post_request(
            instance: TrackerInstance,
            payload: dict,
            action: str,
    ):
        async with aiohttp.ClientSession() as session:
            url = f"{instance.base_url}/{instance.edit_route}"

            payload = {
                "api_key": instance.api_key,
                "action": action,
                "payload": payload
            }
            # logger.debug(url)
            # logger.debug(payload)
            response = await session.post(url, json=payload)

            return await response.json(content_type='text/html')

    async def fetch_offers(self, group: ReplacementGroup, instance: TrackerInstance):
        offer_ids = []
        domains = set()

        json_data = await self.make_tracker_get_request(
            instance=instance,
            page='Offers',
            group=group.offer_group_id
        )

        if not json_data:
            return offer_ids, list(domains)

        if group.offer_geo:
            json_data = [item for item in json_data if item.get('geo').lower() == group.offer_geo.lower()]

        if group.offer_name_regexp_pattern:
            json_data = [
                item for item in json_data if regexp_match(item.get('name').lower(), group.offer_name_regexp_pattern)
            ]

        for off in json_data:
            offer_ids.append(off.get('id'))
            domain = urllib3.util.parse_url(off.get('url')).host
            domains.add(domain)

        return offer_ids, list(domains)

    async def fetch_landings(self, group: ReplacementGroup, instance: TrackerInstance):
        landing_ids = []
        domains = set()

        json_data = await self.make_tracker_get_request(
            instance=instance,
            page='Landing_page',
            group=group.land_group_id
        )

        if not json_data:
            return landing_ids, list(domains)

        if group.land_language:
            json_data = [item for item in json_data if item.get('lang').lower() == group.land_language.lower()]

        if group.land_name_regexp_pattern:
            json_data = [item for item in json_data if regexp_match(item.get('name'), group.land_name_regexp_pattern)]

        for land in json_data:
            landing_ids.append(land.get('id'))
            domain = urllib3.util.parse_url(land.get('url')).host
            domains.add(domain)

        return landing_ids, list(domains)

    async def change_offers_domain(self, offer_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> str:
        if not offer_ids:
            logger.debug(f'No offers to change')
            return ""

        json_data = await self.make_tracker_post_request(
            instance=instance,
            action="offer@mass_edit",
            payload={
                "options": {
                    "domain": new_domain.name,
                },
                "offers": offer_ids,
            }
        )

        return json_data

    async def change_landings_domain(self, landings_ids, new_domain: ProxyDomain, instance: TrackerInstance) -> str:
        if not landings_ids:
            logger.debug(f'No landings to change')
            return ""

        json_data = await self.make_tracker_post_request(
            instance=instance,
            action="landing@mass_edit",
            payload={
                "options": {
                    "domain": new_domain.name,
                },
                "landings": landings_ids,
            }
        )

        return json_data


class ReplacementGroupService(BaseService):
    def __init__(self):
        super().__init__(repo=ReplacementGroupRepository(model=ReplacementGroup))

    async def proxy_change(self, ctx: AppContext, replacement_group_ids: list[int]):
        """ Function to run domain replacement for specific replacement groups with group validation """

        groups: list[ReplacementGroup] = await self.repo.filter(
            id__in=replacement_group_ids,
            prefetch_related=['tracker_instance']
        )

        not_exist_groups = list(
            set.symmetric_difference(set(replacement_group_ids), set([group.pk for group in groups]))
        )

        if len(not_exist_groups) > 0:
            logger.warning(f"Run replacement_group_proxy_change task ERROR: Group ids: {not_exist_groups} not exists")

        not_active_groups = [group.pk for group in groups if not group.is_active]

        if len(not_active_groups) > 0:
            logger.warning(f"Run replacement_group_proxy_change task ERROR: Group ids: {not_active_groups} not active")

        active_groups = [group for group in groups if group.is_active]

        if len(active_groups) > 0:
            await ProxyDomainService().change_domain(ctx, active_groups)
        else:
            logger.warning(f"Run replacement_group_proxy_change task ERROR: Nothing to run")

    async def check_replacement_group(self, replacement_group_id: int):
        replacement_group: ReplacementGroup = await self.get(id=replacement_group_id, prefetch_related=['tracker_instance'])

        offer_ids, _ = await TrackerInstanceService().fetch_offers(
            replacement_group,
            replacement_group.tracker_instance
        )

        landing_ids, _ = await TrackerInstanceService().fetch_landings(
            replacement_group,
            replacement_group.tracker_instance
        )

        return {
            "offers": offer_ids,
            "landing": landing_ids
        }


class ProxyDomainService(BaseService):
    def __init__(self):
        super().__init__(repo=ProxyDomainRepository(model=ProxyDomain))
        self.history = ReplacementHistoryRepository(model=ReplacementHistory)

    async def get_history_domains(
            self,
            prefetch_related: list[str] = None,
            params: AbstractParams = None,
            **filters
    ) -> PageResponse:
        queryset = await self.history.filter_queryable(prefetch_related, **filters)
        return await self.history.paginate(queryset=queryset, params=params)

    async def get_new_domains(self, group: ReplacementGroup):
        # get all domains for specific group
        subfilter = await self.history.filter_queryable(replacement_group_id=group.pk)
        subfilter_values = subfilter.values('to_domain_id')

        # get domains except id that was used
        query = await self.repo.filter_queryable(
            id__not_in=Subquery(subfilter_values)
        )

        result = await query

        return result

    async def get_new_domain_for_selected_groups(self, groups: list[ReplacementGroup]) -> ProxyDomain:
        group_ids = [group.pk for group in groups]

        # For every group we get available domains that was not used previously
        available_domains_for_group = {}
        for group in groups:
            available_domains_for_group[group.name] = await self.get_new_domains(group=group)

        group_items_sets = [set(item) for item in available_domains_for_group.values() if item]

        if not group_items_sets:
            raise NotFound(f"Not found available domains for groups: {group_ids}")

        # In available domains find domain that available for all groups
        intersection = set.intersection(*group_items_sets)

        # logger.debug(intersection)

        new_domain = intersection.pop()

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

    async def change_domain(self, ctx: AppContext, groups: list[ReplacementGroup]) -> dict:
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
            offers, old_offers_domains = await TrackerInstanceService().fetch_offers(group=group, instance=instance)
            landings, old_land_domains = await TrackerInstanceService().fetch_landings(group=group, instance=instance)

            offer_response = await TrackerInstanceService().change_offers_domain(offers, new_domain, instance=instance)
            logger.debug(
                f'Group: {group}, new domain: {new_domain}, offers: {offers}, result: {offer_response}'
            )

            landing_response = await TrackerInstanceService().change_landings_domain(
                landings, new_domain, instance=instance
            )
            logger.debug(
                f'Group: {group}, new domain: {new_domain}, landings: {landings}, result: {landing_response}'
            )

            await Eventory.publish(
                Message(body={
                    'group_name': group.name,
                    'new_domain': new_domain.name,
                    'old_domains': old_offers_domains + old_land_domains
                }),
                ctx.routing_keys.DOMAIN_CHANGED,
                ctx.app_name
            )

            await self.add_history_record(
                new_domain=new_domain,
                previous_domains=old_offers_domains + old_land_domains,
                offers_list=offers,
                lands_list=landings,
                replaced_by=ctx.user,
                replacement_group=group
            )

            change_result['new_domain'] = new_domain.name

            change_result[group.name] = dict()
            change_result[group.name]['offers'] = {
                'ids': offers,
                'result': offer_response
            }
            change_result[group.name]['landings'] = {
                'ids': landings,
                'result': landing_response
            }

        return change_result

    async def add_history_record(
            self,
            new_domain: ProxyDomain,
            previous_domains: list[ProxyDomain],
            offers_list: list[int],
            lands_list: list[int],
            replaced_by: 'User',
            replacement_group: ReplacementGroup
    ):
        previous_domains_models: list[ProxyDomain] = await self.repo.filter(
            name__in=previous_domains
        )

        new_record: ReplacementHistory = await self.history.create(data=dict(
            offers=offers_list,
            lands=lands_list,
            replaced_by=replaced_by,
            to_domain=new_domain,
            replacement_group=replacement_group
        ))

        await new_record.from_domains.add(*previous_domains_models)

    async def create_bulk(self, proxy_domains_in: list[ProxyDomainCreateModel]) -> list[ProxyDomain]:
        list_objects = [
            await self.create(proxy_domain_in) for proxy_domain_in in proxy_domains_in
        ]
        return list_objects


class LeadRecordService(BaseService):
    def __init__(self):
        super().__init__(repo=LeadRecordRepository(model=LeadRecord))

    async def add_new_record(self, ctx: AppContext, new_lead: LeadRecordModel):
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

        await self.repo.create(
            **new_lead
        )

        await Eventory.publish(
            obj=Message(
                source_type=Message.Source.EXTRA,
                data_type=Message.Data.INFO,
                recipient=Recipient(user_id=1),
                body=new_lead.dict(),
            ),
            routing_key=ctx.routing_keys.NEW_LEAD,
            app_name=ctx.app_name
        )

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

        #logging.debug(last_geo_lead)

        time_since_last_lead = int((now - last_geo_lead.time).total_seconds())

        if time_since_last_lead >= max_time_since_last_lead:
            logger.debug(
                f"[{user_tag}] Time since last lead: {time_since_last_lead} exceed maximum: {max_time_since_last_lead}"
            )

        return time_since_last_lead
