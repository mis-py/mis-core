import asyncio
from loguru import logger

from ..config import ModuleSettings
from core.utils.module.components import ScheduledTasks
from core.utils.app_context import AppContext
from libs.eventory import Eventory

scheduled_tasks = ScheduledTasks()
config = ModuleSettings()


@scheduled_tasks.schedule_task(seconds=config.TICK_N_SEC, autostart=True)
async def dummy_task(ctx: AppContext, logger, **kwargs):
    logger.debug(
        f"Execute task every {config.TICK_N_SEC} seconds for module {ctx.app_name} "
        f"and sending message to eventory"
    )
    yield "yield test 1"
    await Eventory.publish(
        body={"dummy_setting": ctx.variables.PRIVATE_SETTING},
        routing_key=ctx.routing_keys.DUMMY_EVENT,
        channel_name=ctx.app_name,
    )
    yield "yield test 2"


@scheduled_tasks.schedule_task(trigger=None)
async def dummy_manual_task(
        ctx: AppContext,
        logger,
        dummy_argument: str,
        dummy_second: int,
        dummy_kwarg: bool = True,
        **kwargs,
):
    body = {
        "dummy_argument": dummy_argument,
        "dummy_second": dummy_second,
        "dummy_kwarg": dummy_kwarg
    }
    logger.debug(
        f"Task is created manually by user with specified trigger "
        f"and sending message '{body}' to eventory"
    )
    await Eventory.publish(
        body=body,
        routing_key=ctx.routing_keys.DUMMY_MANUAL_EVENT,
        channel_name=ctx.app_name,
    )


@scheduled_tasks.schedule_task(trigger=None, single_instance=True)
async def dummy_single_task(ctx: AppContext, logger, **kwargs):
    logger.debug(
        f"Task for single_instance demonstration for {ctx.app_name}"
    )
