from core.utils.module import AppContext
from libs.modules.components import ScheduledTasks
from ..service import ReplacementGroupService

scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def single_replacement_group_proxy_change(ctx: AppContext, replacement_group_id: int):
    """Tasks that run only single replacement group."""
    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=[replacement_group_id],
        # TODO pass to context some data about running job
        reason="Automatic task"
    )


@scheduled_tasks.schedule_task(trigger=None)
async def multiple_replacement_group_proxy_change(ctx: AppContext, replacement_group_ids: list[int]):
    """
    Task that can run multiple groups at same time.
    Main purpose is that we can assign single domain on multiple groups at single run.
    """
    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=replacement_group_ids,
        reason="Automatic task"
    )

