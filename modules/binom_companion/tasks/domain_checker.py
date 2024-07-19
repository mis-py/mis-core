from loguru import logger

from core.utils.app_context import AppContext
from core.utils.module.components import ScheduledTasks
from core.utils.scheduler import JobMeta
from ..service import YandexBrowserCheckService, ReplacementGroupService
from ..services.tracker import get_tracker_service
from ...proxy_registry.dependencies.services import get_proxy_service
from ...proxy_registry.services.checker import ProxyChecker

scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def yandex_check_replacement_group_proxy_change(ctx: AppContext, job_meta: JobMeta, replacement_group_ids: list[int], yandex_api_key: str):
    """
    Check ban in the yandex browser of domains that are currently in use
    """

    groups = await ReplacementGroupService().filter(
        id__in=replacement_group_ids,
        prefetch_related=['tracker_instance'],
    )

    all_domains = []
    for group in groups:
        tracker_instance_service = get_tracker_service(tracker_type=group.tracker_instance.tracker_type)
        _, offers_domains = await tracker_instance_service.fetch_offers(
            group=group,
            instance=group.tracker_instance,
        )
        all_domains.extend(offers_domains)

    # check domains is banned in yandex browser
    banned_domains = await YandexBrowserCheckService().check_domains(
        domains=all_domains,
        yandex_api_key=yandex_api_key,
    )

    if not banned_domains:
        logger.debug(f"Group ids: {replacement_group_ids}. Domains not banned: {all_domains}")
        return

    logger.debug(f"Group ids: {replacement_group_ids}. Found banned domains: {all_domains}!")

    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=replacement_group_ids,
        reason=f"Job id: {job_meta.job_id}"
    )


@scheduled_tasks.schedule_task(trigger=None)
async def check_domains_of_replacement_groups(
        ctx: AppContext,
        job_meta: JobMeta,
        replacement_group_ids: list[int],
        proxy_ids: list[int],
):
    proxy_service = get_proxy_service()
    proxies = await proxy_service.filter_by_ids(proxy_ids)
    proxies_address = [proxy.address for proxy in proxies]

    proxy_checker = ProxyChecker()
    valid_proxies = await proxy_checker.filter_valid_proxies(proxies_address)

    if not valid_proxies:
        logger.warning("No valid proxies for check domains!")
        return

    await ReplacementGroupService().check_group_domains(
        ctx=ctx,
        replacement_group_ids=replacement_group_ids,
        proxies=valid_proxies,
    )