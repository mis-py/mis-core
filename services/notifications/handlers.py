from loguru import logger

from services.eventory import CustomIncomingMessage
from services.redis import RedisService

from services.notifications.utils.message import Message, IncomingProcessedMessage
from services.notifications.db_logic import query_users_who_receive_message
from services.notifications.utils import get_or_set_routing_key_cache, body_verbose_by_template


async def eventory_message_handler(eventory_message: CustomIncomingMessage, senders: list, redis: RedisService):
    message = Message.from_dict(eventory_message.json)

    if message.data_type == Message.Data.INTERNAL:
        return

    app_name, routing_key = eventory_message.routing_key.split(':', 1)
    routing_key_cache = await get_or_set_routing_key_cache(redis.cache, routing_key)

    query_users = await query_users_who_receive_message(
        routing_key=routing_key,
        is_force_send=message.is_force_send,
        recipient=message.recipient,
    )
    users = await query_users

    if not users:
        # what message by the way?
        #logger.debug("No users for send message!")
        return

    # make incoming processed message for senders
    key_verbose = routing_key_cache.get("key_verbose")
    body_verbose = body_verbose_by_template(
        body=message.body,
        template_string=routing_key_cache.get("template"),
    )
    processed_message = IncomingProcessedMessage(
        message=message,
        app_name=app_name,
        key=routing_key,
        key_verbose=key_verbose,
        body_verbose=body_verbose,
    )

    for sender in senders:
        logger.debug(f'Run sender: {sender.__name__}')
        await sender(processed_message, users, redis)
