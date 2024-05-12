from services.modules.context import AppContext
from ..service import ReplacementGroupService

from . import scheduled_tasks


@scheduled_tasks.schedule_task(trigger=None)
async def single_replacement_group_proxy_change(ctx: AppContext, replacement_group_id: int):
    """Tasks that run only single replacement group."""
    await ReplacementGroupService().proxy_change(
        ctx=ctx,
        replacement_group_ids=[replacement_group_id]
    )


@scheduled_tasks.schedule_task(trigger=None)
async def multiple_replacement_group_proxy_change(ctx: AppContext, replacement_group_ids: list[int]):
    """
    Task that can run multiple groups at same time.
    Main purpose is that we can assign single domain on multiple groups at single run.
    """
    await ReplacementGroupService().proxy_change(
        ctx=ctx, replacement_group_ids=replacement_group_ids
    )

