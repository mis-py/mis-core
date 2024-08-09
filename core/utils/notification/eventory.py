import functools
from typing import Optional, Callable, get_type_hints

import ujson
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from pydantic import BaseModel

from core.utils.notification.message import EventMessage
from core.utils.notification.recipient import Recipient
from libs.eventory import Eventory


async def eventory_publish(
        body: dict,
        routing_key: str,
        channel_name: str,
        source_type: EventMessage.Source = EventMessage.Source.INTRA,
        data_type: EventMessage.Data = EventMessage.Data.INFO,
        recipient: Optional[Recipient] = None,
        is_force_send: bool = False,
):
    """Make custom event message and publish event"""
    event_message = EventMessage(
        body=body,
        source_type=source_type,
        data_type=data_type,
        recipient=recipient,
        is_force_send=is_force_send,
    )

    await Eventory.publish_event(
        body=event_message.to_dict(),
        routing_key=routing_key,
        channel_name=channel_name,
    )


def inject_and_process_wrapper(func: Callable, extra_kwargs: dict):
    """
    Process message (decode/validate data) before run func (consumer)
    And inject arguments to func (consumer)
    """

    @functools.wraps(func)
    async def receiver(incoming_message: AbstractIncomingMessage, **kwargs):
        async with incoming_message.process():
            dict_data = _body_decode(incoming_message.body)

            try:
                validated_body = _validate_message_body(func, dict_data['body'])
            except ValueError as e:
                logger.warning(f"Validation error event receiving for consumer={incoming_message.consumer_tag}: {e}")
                return

            kwargs['incoming_message'] = incoming_message  # AbstractIncomingMessage (aio_pika object)
            kwargs['message'] = EventMessage.from_dict(dict_data)  # Message (custom dataclass)
            kwargs['validated_body'] = validated_body  # valid pydantic model object
            kwargs.update(extra_kwargs)  # another keyword arguments (ex: AppContext)

            # make keyword argument optional for using in func
            kwargs = _filter_only_using_kwargs(func, kwargs)
            return await func(**kwargs)

    return receiver


def _filter_only_using_kwargs(func: Callable, kwargs: dict) -> dict:
    valid_keys = func.__code__.co_varnames
    return {k: v for k, v in kwargs.items() if k in valid_keys}


def _body_decode(body: bytes) -> dict:
    json_data = ujson.loads(body.decode('utf-8'))
    return json_data


def _validate_message_body(func: Callable, body: dict) -> BaseModel | dict:
    type_hints = get_type_hints(func)
    if issubclass(type_hints.get('validated_body', dict), BaseModel):
        PydanticModel = type_hints['validated_body']
        return PydanticModel(**body)
    else:
        return body