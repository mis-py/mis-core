from loguru import logger

from ..config import ModuleSettings, RoutingKeys
from core.utils.notification import Message
from services.modules.components import ScheduledTasks
from services.modules.context import AppContext
from services.eventory import Eventory

scheduled_tasks = ScheduledTasks()
config = ModuleSettings()
routing_keys = RoutingKeys()


@scheduled_tasks.schedule_task(seconds=config.TICK_5_SEC, autostart=True)
async def template_task(ctx: AppContext):
    logger.debug(
        f"Execute task every {config.TICK_5_SEC} seconds for module {ctx.app_name} "
        f"and sending message to eventory"
    )
    await Eventory.publish(
        Message(
            body={"setting": ctx.settings.PRIVATE_SETTING},
        ),
        routing_keys.EXAMPLE,
        ctx.app_name
    )
