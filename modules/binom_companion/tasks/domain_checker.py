from loguru import logger

from libs.modules.AppContext import AppContext
from libs.modules.components import ScheduledTasks
from ..service import YandexBrowserCheckService, ReplacementGroupService, TrackerInstanceService

scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def domain_ban_monitor(ctx: AppContext, replacement_group_ids: list[int]):
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
        yandex_api_key=ctx.variables.YANDEX_API_KEY,
    )
    if not banned_domains:
        logger.debug(f"Group ids: {replacement_group_ids}. Domains not banned: {all_domains}")
        return

    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=replacement_group_ids,
        reason="Automatic task"
    )
