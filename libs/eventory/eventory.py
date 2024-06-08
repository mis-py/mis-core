import functools
from collections import defaultdict
from typing import Callable, Optional, get_type_hints

from loguru import logger
import ujson
from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractChannel, ExchangeType, AbstractRobustConnection, AbstractIncomingMessage
from aiormq import DuplicateConsumerTag, AMQPConnectionError
from pydantic import BaseModel

from core.utils.notification.message import EventMessage
from core.utils.notification.recipient import Recipient

from .consumer import Consumer
from .config import RabbitSettings

settings = RabbitSettings()


class Eventory:
    # Connection in single per process
    _connection: AbstractRobustConnection

    # Channel per module preferred
    _channels: dict[str, AbstractChannel] = {}

    # Registered consumers
    _consumers: dict[str, list[Consumer]] = defaultdict(list)

    # RabbitMQ exchange name
    _exchange_name: str = 'eventory'

    @classmethod
    async def init(cls):
        try:
            cls._connection = await connect_robust(settings.RABBITMQ_URL)
        except AMQPConnectionError as e:
            logger.warning(f'RabbitMQ connection error. {type(e)}: {e}')
            raise Exception(f'RabbitMQ connection error. {type(e)}: {e}')

    @classmethod
    async def close(cls):
        await cls._connection.close()

    @classmethod
    async def get_channel(cls, name: str) -> AbstractChannel:
        if name not in cls._channels:
            cls._channels[name] = await cls._connection.channel()
        return cls._channels[name]

    @classmethod
    async def remove_channel(cls, name: str) -> None:
        if name in cls._channels:
            await cls._channels[name].close()
            del cls._channels[name]

    @classmethod
    async def register_consumer(
            cls,
            func: Callable,
            routing_key: str,
            channel_name: str,
            tag: str = None,
            extra_kwargs: dict = None,
    ) -> Consumer:
        """
        Consumer is message receiver, can be declared for any function
        :param channel_name:
        :param routing_key:
        :param func: Consumer func
        :param tag: Tag for consumer
        :param extra_kwargs: Keyword arguments which will inject to func
        :return:
        """
        if extra_kwargs is None:
            extra_kwargs = {}

        if tag is None:
            # channel_name + func_name to avoid duplication
            tag = f"{channel_name}:{func.__name__}"

        # inject params to func
        receiver = cls._inject_and_process_wrapper(func, extra_kwargs)

        channel = await cls.get_channel(channel_name)
        exchange = await channel.declare_exchange(cls._exchange_name, type=ExchangeType.DIRECT, auto_delete=True)
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange, routing_key=routing_key)

        try:
            consumer = Consumer(queue, receiver, tag)
            cls._consumers[channel_name].append(consumer)
            return consumer
        except DuplicateConsumerTag:
            raise RuntimeError(f'Duplicated consumer_tag: "{tag}"')

    @classmethod
    async def publish(
            cls,
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

        await cls._publish_event(
            body=event_message.to_dict(),
            routing_key=routing_key,
            channel_name=channel_name,
        )

    @classmethod
    async def _publish_event(cls, body: dict, routing_key: str, channel_name: str):
        channel = await cls.get_channel(channel_name)
        exchange = await channel.declare_exchange(
            name=cls._exchange_name,
            type=ExchangeType.DIRECT,
            auto_delete=True,
        )

        message = Message(
            body=ujson.dumps(body, ensure_ascii=False).encode('utf-8'),
            content_type='application/json',
            content_encoding='utf-8'
        )
        return await exchange.publish(
            message=message,
            routing_key=routing_key,
        )

    @classmethod
    def iter_consumers(cls):
        # module consumers
        for channel_name, consumers in cls._consumers.items():
            for consumer in consumers:
                yield channel_name, consumer

    @classmethod
    def get_consumer(cls, consumer_tag: str) -> tuple[str, Consumer] | tuple[None, None]:
        for channel_name, consumer in cls.iter_consumers():
            if consumer.consumer_tag == consumer_tag:
                return channel_name, consumer
        return None, None

    @classmethod
    async def pause_consumer(cls, consumer_tag: str) -> bool:
        channel_name, consumer = cls.get_consumer(consumer_tag)
        if consumer:
            await consumer.stop()
            return True
        return False

    @classmethod
    async def resume_consumer(cls, consumer_tag: str) -> bool:
        channel_name, consumer = cls.get_consumer(consumer_tag)
        if consumer:
            await consumer.start()
            return True
        return False

    @classmethod
    def _inject_and_process_wrapper(cls, func: Callable, extra_kwargs: dict):
        """
        Process message (decode/validate data) before run func (consumer)
        And inject arguments to func (consumer)
        """

        @functools.wraps(func)
        async def receiver(incoming_message: AbstractIncomingMessage, **kwargs):
            async with incoming_message.process():
                dict_data = cls._body_decode(incoming_message.body)

                try:
                    validated_body = cls._validate_message_body(func, dict_data['body'])
                except ValueError as e:
                    logger.warning(f"Validation error event receiving for consumer={incoming_message.consumer_tag}: {e}")
                    return

                kwargs['incoming_message'] = incoming_message  # AbstractIncomingMessage (aio_pika object)
                kwargs['message'] = EventMessage.from_dict(dict_data)  # Message (custom dataclass)
                kwargs['validated_body'] = validated_body  # valid pydantic model object
                kwargs.update(extra_kwargs)  # another keyword arguments (ex: AppContext)

                # make keyword argument optional for using in func
                kwargs = cls._filter_only_using_kwargs(func, kwargs)
                return await func(**kwargs)

        return receiver

    @classmethod
    def _filter_only_using_kwargs(cls, func, kwargs) -> dict:
        valid_keys = func.__code__.co_varnames
        return {k: v for k, v in kwargs.items() if k in valid_keys}

    @classmethod
    def _body_decode(cls, body: bytes) -> dict:
        json_data = ujson.loads(body.decode('utf-8'))
        return json_data

    @classmethod
    def _validate_message_body(cls, func, body: dict) -> BaseModel | dict:
        type_hints = get_type_hints(func)
        if issubclass(type_hints.get('validated_body', dict), BaseModel):
            PydanticModel = type_hints['validated_body']
            return PydanticModel(**body)
        else:
            return body
