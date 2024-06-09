from core.utils.app_context import AppContext
from core.utils.module.components import ScheduledTasks
from core.utils.scheduler import JobMeta

from ..service import ReplacementGroupService

scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def single_replacement_group_proxy_change(ctx: AppContext, job_meta: JobMeta, replacement_group_id: int):
    """Tasks that run only single replacement group."""
    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=[replacement_group_id],
        reason=f"Job id: {job_meta.job_id}"
    )


@scheduled_tasks.schedule_task(trigger=None)
async def multiple_replacement_group_proxy_change(ctx: AppContext, job_meta: JobMeta, replacement_group_ids: list[int]):
    """
    Task that can run multiple groups at same time.
    Main purpose is that we can assign single domain on multiple groups at single run.
    """
    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=replacement_group_ids,
        reason=f"Job id: {job_meta.job_id}"
    )

