from loguru import logger

from core.utils.notification.message import Message
from ..config import ModuleSettings, RoutingKeys
from services.modules.components import ScheduledTasks
from services.modules.context import AppContext
from services.eventory import Eventory

scheduled_tasks = ScheduledTasks()
config = ModuleSettings()
routing_keys = RoutingKeys()


@scheduled_tasks.schedule_task(seconds=config.TICK_5_SEC, autostart=True)
async def dummy_task(ctx: AppContext):
    logger.debug(
        f"Execute task every {config.TICK_5_SEC} seconds for module {ctx.app_name} "
        f"and sending message to eventory"
    )
    await Eventory.publish(
        Message(
            body={"dummy_setting": ctx.settings.PRIVATE_SETTING},
        ),
        routing_keys.DUMMY_EVENT,
        ctx.app_name
    )


@scheduled_tasks.schedule_task(trigger=None)
async def dummy_manual_task(ctx: AppContext, dummy_argument: str):
    logger.debug(
        f"Task is created manually by user with specified trigger "
        f"and sending message '{dummy_argument}' to eventory"
    )
    await Eventory.publish(
        Message(
            body={"dummy_argument": dummy_argument},
        ),
        routing_keys.DUMMY_MANUAL_EVENT,
        ctx.app_name
    )


@scheduled_tasks.schedule_task(trigger=None, single_instance=True)
async def dummy_single_task(ctx: AppContext):
    logger.debug(
        f"Task for single_instance demonstration for {ctx.app_name}"
    )
