from types import SimpleNamespace

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


@event_consumers.add_consumer(routing_keys.DUMMY_EDIT_EVENT)
async def test_consumer(ctx: AppContext, message: Message, data: SimpleNamespace):
    logger.warning(f"Dummy edit: '{data.body.dummy_string}' for module: {ctx.app_name}")
