from loguru import logger

from core.utils.notification.message import Message
from libs.modules.components import EventManager
from libs.modules.AppContext import AppContext
from ..config import RoutingKeys

routing_keys = RoutingKeys()
event_consumers = EventManager()


@event_consumers.add_consumer(routing_keys.DUMMY_EVENT)
async def template_consumer(ctx: AppContext, message: Message):
    logger.debug(f"Received message: {message.json} for module: {ctx.app_name}")
