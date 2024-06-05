import functools
from types import SimpleNamespace
from typing import Type, Callable

import ujson
from loguru import logger
from pydantic import BaseModel

from core.utils.notification.message import Message
from libs.eventory import Eventory


class EventoryService:
    def __init__(self, eventory: Type[Eventory]):
        self.eventory = eventory

    async def publish(
            self,
            schema: BaseModel,
            routing_key: str,
            module_name: str,
            source_type: Message.Source = Message.Source.INTRA,
            data_type: Message.Data = Message.Data.INFO,
            is_force_send: bool = False,
    ):
        await self.eventory.publish(
            data=Message(
                body=schema.model_dump(),
                source_type=source_type,
                data_type=data_type,
                is_force_send=is_force_send,
            ).to_dict(),
            routing_key=routing_key,
            channel_name=module_name
        )
        logger.info(f"Published event {routing_key}")

    async def register_consumer(self, func: Callable, key: str, module_name: str, params_to_inject: dict,
                                tag: str = None):
        if tag is None:
            # module_name + func_name to avoid duplication
            tag = f"{module_name}:{func.__name__}"

        # inject params to func
        receiver = self._inject_params(func, params_to_inject)

        return await self.eventory.register_consumer(
            receiver=receiver,
            routing_key=key,
            channel_name=module_name,
            tag=tag,
        )

    def _inject_params(self, func: Callable, to_inject: dict):
        @functools.wraps(func)
        async def receiver(message, **kwargs):
            async with message.process():
                data = self._body_to_namespace(message.body)

                kwargs['message'] = message
                kwargs['data'] = data
                kwargs.update(to_inject)

                # make keyword argument optional for using in func
                kwargs = self._filter_only_using_kwargs(func, kwargs)
                return await func(**kwargs)

        return receiver

    def _filter_only_using_kwargs(self, func, kwargs):
        valid_keys = func.__code__.co_varnames
        return {k: v for k, v in kwargs.items() if k in valid_keys}

    def _body_to_namespace(self, body: bytes) -> SimpleNamespace:
        json_data = ujson.loads(body.decode('utf-8'))
        data = SimpleNamespace(**json_data)
        if isinstance(data.body, dict):
            data.body = SimpleNamespace(**data.body)
        return data
