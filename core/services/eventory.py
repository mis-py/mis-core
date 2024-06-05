import functools
from typing import Type, Callable, get_type_hints, Optional

import ujson
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from pydantic import BaseModel

from core.utils.notification.message import Message
from core.utils.notification.recipient import Recipient
from libs.eventory import Eventory


class EventoryService:
    def __init__(self, eventory: Type[Eventory]):
        self.eventory = eventory

    async def publish(
            self,
            body: dict,
            routing_key: str,
            module_name: str,
            source_type: Message.Source = Message.Source.INTRA,
            data_type: Message.Data = Message.Data.INFO,
            recipient: Optional[Recipient] = None,
            is_force_send: bool = False,
    ):
        message = Message(
            body=body,
            source_type=source_type,
            data_type=data_type,
            recipient=recipient,
            is_force_send=is_force_send,
        )

        await self.eventory.publish(
            data=message.to_dict(),
            routing_key=routing_key,
            channel_name=module_name
        )
        logger.info(f"Published event {routing_key}")

    async def register_consumer(
            self,
            func: Callable,
            routing_key: str,
            module_name: str,
            extra_kwargs: dict,
            tag: str = None,
    ):
        if tag is None:
            # module_name + func_name to avoid duplication
            tag = f"{module_name}:{func.__name__}"

        # inject params to func
        receiver = self._inject_and_process_wrapper(func, extra_kwargs)

        return await self.eventory.register_consumer(
            receiver=receiver,
            routing_key=routing_key,
            channel_name=module_name,
            tag=tag,
        )

    def _inject_and_process_wrapper(self, func: Callable, extra_kwargs: dict):
        """
        Process message (decode/validate data) before run func (consumer)
        And inject arguments to func (consumer)
        """

        @functools.wraps(func)
        async def receiver(message: AbstractIncomingMessage, **kwargs):
            async with message.process():
                dict_data = self._body_decode(message.body)

                try:
                    validated_body = self._validate_message_body(func, dict_data['body'])
                except ValueError as e:
                    logger.warning(f"Validation error when receiving message for consumer={message.consumer_tag}: {e}")
                    return

                kwargs['incoming_message'] = message  # AbstractIncomingMessage (aio_pika object)
                kwargs['message'] = Message.from_dict(dict_data)  # Message (custom dataclass)
                kwargs['validated_body'] = validated_body  # valid pydantic model object
                kwargs.update(extra_kwargs)  # another keyword arguments (ex: AppContext)

                # make keyword argument optional for using in func
                kwargs = self._filter_only_using_kwargs(func, kwargs)
                return await func(**kwargs)

        return receiver

    def _filter_only_using_kwargs(self, func, kwargs) -> dict:
        valid_keys = func.__code__.co_varnames
        return {k: v for k, v in kwargs.items() if k in valid_keys}

    def _body_decode(self, body: bytes) -> dict:
        json_data = ujson.loads(body.decode('utf-8'))
        return json_data

    def _validate_message_body(self, func, body: dict) -> BaseModel | dict:
        type_hints = get_type_hints(func)
        if issubclass(type_hints.get('validated_body', dict), BaseModel):
            PydanticModel = type_hints['validated_body']
            return PydanticModel(**body)
        else:
            return body
