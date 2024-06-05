import asyncio
import functools
from asyncio import Task
from collections import defaultdict
from typing import Callable

from loguru import logger
import ujson
from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractChannel, ExchangeType, AbstractRobustConnection
from aiormq import DuplicateConsumerTag, AMQPConnectionError

from core.repositories.routing_key import RoutingKeyRepository
from core.services.notification import RoutingKeyService

from .consumer import Consumer
from .config import RabbitSettings
from .utils import RoutingKeysSet
from ..modules import AppContext

settings = RabbitSettings()


class Eventory:
    # Connection in single per process
    _connection: AbstractRobustConnection

    # Channel per module preferred
    _channels: dict[str, AbstractChannel] = {}

    # Registered consumers
    _consumers: dict[str, list[Consumer]] = defaultdict(list)

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
    async def register_consumer(cls, receiver: Callable, routing_key: str, channel_name: str, tag: str) -> Consumer:
        """
        Consumer is message receiver, can be declared for any function
        :param channel_name:
        :param routing_key:
        :param receiver:
        :param tag: - Tag for consumer
        :return:
        """
        channel = await cls.get_channel(channel_name)
        exchange = await channel.declare_exchange("eventory", type=ExchangeType.DIRECT, auto_delete=True)
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange, routing_key=routing_key)

        try:
            consumer = Consumer(queue, receiver, tag)
            cls._consumers[channel_name].append(consumer)
            return consumer
        except DuplicateConsumerTag:
            raise RuntimeError(f'Duplicated consumer_tag: "{tag}"')

    @classmethod
    async def publish(cls, data: dict, routing_key: str, channel_name: str):
        message = Message(
            body=ujson.dumps(data, ensure_ascii=False).encode('utf-8'),
            content_type='application/json',
            content_encoding='utf-8'
        )
        channel = await cls.get_channel(channel_name)
        exchange = await channel.declare_exchange(
            name="eventory",
            type=ExchangeType.DIRECT,
            auto_delete=True,
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
    async def make_routing_keys_set(cls, app):
        routing_key_service = RoutingKeyService(routing_key_repo=RoutingKeyRepository())

        routing_keys = await routing_key_service.filter(app_id=app.pk)

        return RoutingKeysSet(routing_keys)
