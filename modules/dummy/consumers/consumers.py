from loguru import logger


from core.utils.notification.message import EventMessage
from core.utils.module.components import EventManager
from core.utils.app_context import AppContext

from ..config import RoutingKeys
from ..db.schema import DummyResponse

routing_keys = RoutingKeys()
event_consumers = EventManager()


@event_consumers.add_consumer(routing_keys.DUMMY_EVENT)
# TODO what if we put dependency resolve in args? like those in fastapi routes
async def template_consumer(ctx: AppContext, message: EventMessage):
    logger.debug(f"Received message: {message.body} for module: {ctx.app_name}")


@event_consumers.add_consumer(routing_keys.DUMMY_EDIT_EVENT)
async def dummy_edit_consumer(ctx: AppContext, message: EventMessage):
    try:
        dummy_id = message.body['id']
        dummy_string = message.body['dummy_string']
        logger.debug(f"[{ctx.app_name}] Received event: Dummy edit - {dummy_id=} {dummy_string=}")
    except KeyError as e:
        logger.warning(f"[{ctx.app_name}] Received event error: KeyError {e}")


@event_consumers.add_consumer(routing_keys.DUMMY_EDIT_EVENT)
async def dummy_edit_consumer_with_pydantic_validation(ctx: AppContext, validated_body: DummyResponse):
    dummy_id = validated_body.id
    dummy_string = validated_body.dummy_string
    logger.debug(f"[{ctx.app_name}] Received event: Dummy edit - {dummy_id=} {dummy_string=}")

