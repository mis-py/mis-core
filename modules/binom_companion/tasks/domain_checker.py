from loguru import logger

from core.utils.app_context import AppContext
from core.utils.module.components import ScheduledTasks
from core.utils.scheduler import JobMeta
from ..service import YandexBrowserCheckService, ReplacementGroupService
from ..services.tracker import get_tracker_service

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
        tracker_instance_service = get_tracker_service(type=group.tracker_instance.type)
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
