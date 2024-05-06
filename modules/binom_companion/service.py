from datetime import datetime, timedelta, timezone
from loguru import logger
from tortoise.expressions import Subquery

from core.utils.notification.message import Message
from services.eventory import Eventory

from core.dependencies.misc import PaginateParamsDep
from core.services.base.base_service import BaseService
from services.modules.context import AppContext
from .db.schemas import GeoCreateModel
from .repository import (
    BinomCompanionGeoRepository,
    BinomCompanionDomainRepository,
    TrackerInstanceRepository,
    ReplacementGroupRepository,
    ProxyDomainRepository,
    ReplacementHistoryRepository,
    LeadRecordRepository
)
from .db.models import (
    BinomGeo,
    Domain,
    TrackerInstance,
    ReplacementGroup,
    ProxyDomain,
    ReplacementHistory,
    LeadRecord
)
from .util.util import fetch_offers, fetch_landings, change_offers_domain, change_landings_domain


class TrackerInstanceService(BaseService):
    def __init__(self):
        super().__init__(repo=TrackerInstanceRepository(model=TrackerInstance))


class ReplacementGroupService(BaseService):
    def __init__(self):
        super().__init__(repo=ReplacementGroupRepository(model=ReplacementGroup))


class ProxyDomainService(BaseService):
    def __init__(self):
        super().__init__(repo=ProxyDomainRepository(model=ProxyDomain))
        self.history = ReplacementHistoryRepository(model=ReplacementHistory)

    async def get_history_domains(self, paginate_params: PaginateParamsDep):
        pass
        # return self.history.filter_and

    async def get_fresh_domains(self, group: ReplacementGroup):
        subfilter = await self.history.filter_queryable(replacement_group_id__not=group.pk)
        subfilter_values = subfilter.values('to_domain_id')

        return await self.repo.filter(
            id__not_in=Subquery(subfilter_values)
        )

        # async def get_available_domain(geo_id: int) -> (Domain, None):
        #     available_status = [DomainStatus.DONE, DomainStatus.REUSE]
        #     geo_allowed_domains = set(await Domain.filter(allowed_geo=geo_id, status__in=available_status))
        #     geo_banned_domains = set(await Domain.filter(banned_geo=geo_id, status__in=available_status))
        #     available_domains = geo_allowed_domains - geo_banned_domains
        #     if available_domains:
        #         return available_domains.pop()

    async def is_change_domain_cooldown_pass(self, replacement_group_id: int, cooldown: int):
        """
        Search for last used domain in specific replacement group and compare with cooldown value.

        :param replacement_group_id:
        :param cooldown:
        :return:
        """
        now = datetime.now(timezone.utc)
        last_changed_domain = (await self.history.filter(replacement_group_id=replacement_group_id))\
            .order_by('-date_changed').first()

        if last_changed_domain and last_changed_domain.date_changed > now - timedelta(seconds=cooldown):
            return False
        return True

    async def change_domain(self, ctx: AppContext, groups: list [ReplacementGroup]):

        group_names = [group.name for group in groups]
        logger.debug(f"Run replacement_group_proxy_change task for groups: {group_names}")

        # For every group we get available domains that was not used previously
        available_group_domains = {}
        for group in groups:
            available_group_domains[group.name] = await self.get_fresh_domains(group=group)

        group_items = available_group_domains.values()

        # In available domains find domain that available for all groups
        intersection = set.intersection(*group_items)

        new_domain = intersection.pop()

        if not new_domain:
            return "Not found new domain!!"

        for group in groups:
            instance = group.tracker_instance
            offers, old_offers_domains = await fetch_offers(group=group, instance=instance)
            landings, old_land_domains = await fetch_landings(group=group, instance=instance)

            await change_offers_domain(offers, new_domain, instance=instance)
            logger.debug(f'Group: {group.name} Set new domain for offers: {new_domain}')

            await change_landings_domain(landings, new_domain, instance=instance)
            logger.debug(f'Group: {group.name} Set new domain for landings: {new_domain}')

            await Eventory.publish(
                Message(body={
                    'group_name': group.name,
                    'new_domain': new_domain,
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
                replaced_by=ctx.user.pk,
            )

    async def add_history_record(
            self,
            new_domain: ProxyDomain,
            previous_domains: list[ProxyDomain],
            offers_list: list[int],
            lands_list: list[int],
            replaced_by: 'User'
    ):

        # This part change status for domain to active
        # await update_domain_status(
        #     row_index=new_domain_row.index,
        #     column_index=geo.status,
        #     status=DomainStatus.ACTIVE,
        #     domain=new_domain_row.domain,
        #     variables=variables,
        #     geo_names=geo_names,
        # )
        await self.history.create(data=dict(
            offers=offers_list,
            lands=lands_list,
            replaced_by=replaced_by.pk,
            to_domain=new_domain,
            from_domains=previous_domains
        ))

        # this part mark for domain new current geo (group)
        # await update_domain_current_geo(
        #     current_geo=current_geo,
        #     row_index=new_domain_row.index,
        #     column_index=geo.curr_geo,
        #     previous_index=previous_domain_row.index if previous_domain_row else None,
        #     domain=new_domain_row.domain,
        #     variables=variables,
        #     geo_names=geo_names,
        # )

        # if previous_domains:
            # set used by default for prev domains
            # status = DomainStatus.USED
            # if domain was used in other group set REUSE
            # if not previous_domain_row.is_another_ban:
            #     status = DomainStatus.REUSE

            # set new status for prev domains
            # await update_domain_status(
            #     row_index=previous_domain_row.index,
            #     column_index=geo.status,
            #     status=status,
            #     domain=previous_domain_row.domain,
            #     variables=variables,
            #     geo_names=geo_names,
            # )

            # this maybe set domain as banned if all geos is banned
            # await set_ban_domain(
            #     geo_name=geo.name,
            #     row_index=previous_domain_row.index,
            #     column_index=geo.ban,
            #     domain=previous_domain_row.domain,
            #     variables=variables,
            # )

        # await ChangedDomain.create(
        #     from_domains=",".join(list(set(offers_domains + land_domains))),
        #     to_domain=new_domain_row.domain,
        #     geo=geo.name,
        #     offers=offers
        # )


class LeadRecordService(BaseService):
    def __init__(self):
        super().__init__(repo=LeadRecordRepository(model=LeadRecord))

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

    async def check_last_lead_time_by_geo(self, geo: BinomGeo, max_time_since_last_lead):
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
