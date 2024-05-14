from string import Template
from loguru import logger
from core.db.models import RoutingKey
from loguru import logger

from libs.eventory import CustomIncomingMessage
from libs.redis import RedisService

from .message import Message, IncomingProcessedMessage
from ...dependencies.services import get_user_service
from ...services.user import UserService


async def eventory_message_handler(eventory_message: CustomIncomingMessage, senders: list, redis: RedisService):
    message = Message.from_dict(eventory_message.json)

    if message.data_type == Message.Data.INTERNAL:
        return

    app_name, routing_key = eventory_message.routing_key.split(':', 1)
    routing_key_cache = await get_or_set_routing_key_cache(redis.cache, routing_key)

    user_service: UserService = get_user_service()
    users = await user_service.users_who_receive_message(
        routing_key=routing_key,
        is_force_send=message.is_force_send,
        recipient=message.recipient,
    )

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


def body_verbose_by_template(body, template_string: str):
    """Format body dict to string using Template string"""
    if not template_string:
        return None

    try:
        template = Template(template_string)
        return template.substitute(body)
    except KeyError as error:
        logger.error(f"Wrong template string key: {error}")
        return None


async def get_or_set_routing_key_cache(cache, routing_key: str):
    cache_name = "routing_key"

    # get
    value = await cache.get_json(cache_name=cache_name, key=routing_key)
    if value:
        return value

    # set
    key_instance = await RoutingKey.get_or_none(name=routing_key)
    value = routing_key_to_dict(key_instance)
    await cache.set_json(
        cache_name=cache_name,
        key=routing_key,
        value=value,
    )
    return value


def routing_key_to_dict(instance: RoutingKey) -> dict:
    value = {
        "key_verbose": instance.key_verbose,
        "template": instance.template,
    }
    return value
