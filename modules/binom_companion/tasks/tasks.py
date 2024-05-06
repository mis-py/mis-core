from services.modules.components import ScheduledTasks
from services.modules.context import AppContext
from ..util.proxy_change import proxy_change


scheduled_tasks = ScheduledTasks()


@scheduled_tasks.schedule_task(trigger=None)
async def single_replacement_group_proxy_change(ctx: AppContext, replacement_group_id: int):
    """Tasks that run only single replacement group."""
    await proxy_change(ctx=ctx, replacement_group_ids=[replacement_group_id])


@scheduled_tasks.schedule_task(trigger=None)
async def multiple_replacement_group_proxy_change(ctx: AppContext, replacement_group_id: list[int]):
    """
    Task that can run multiple groups at same time.
    Main purpose is that we can assign single domain on multiple groups at single run.
    """
    await proxy_change(ctx=ctx, replacement_group_ids=replacement_group_id)

