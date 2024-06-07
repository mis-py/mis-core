from loguru import logger

from core.utils.module import AppContext
from libs.modules.components import ScheduledTasks
from ..service import YandexBrowserCheckService, ReplacementGroupService, TrackerInstanceService

scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def yandex_check_replacement_group_proxy_change(ctx: AppContext, replacement_group_ids: list[int], yandex_api_key: str):
    """
    Check ban in the yandex browser of domains that are currently in use
    """

    groups = await ReplacementGroupService().filter(
        id__in=replacement_group_ids,
        prefetch_related=['tracker_instance'],
    )

    all_domains = []
    for group in groups:
        _, offers_domains = await TrackerInstanceService().fetch_offers(
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

    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=replacement_group_ids,
        reason="Automatic task"
    )
