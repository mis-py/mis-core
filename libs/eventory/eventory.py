from collections import defaultdict
from typing import Callable

from loguru import logger
import ujson
from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractChannel, ExchangeType, AbstractRobustConnection
from aiormq import DuplicateConsumerTag, AMQPConnectionError

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

    # RabbitMQ exchange name and type
    _exchange_name: str = 'topic_eventory'
    _exchange_type: ExchangeType = ExchangeType.TOPIC

    @classmethod
    async def init(cls):
        try:
            cls._connection = await connect_robust(settings.RABBITMQ_URI)
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
    ) -> Consumer:
        """
        Consumer is message receiver, can be declared for any function
        :param channel_name:
        :param routing_key:
        :param func: Consumer func
        :param tag: Tag for consumer
        :return:
        """
        if tag is None:
            # channel_name + func_name to avoid duplication
            tag = f"{channel_name}:{func.__name__}"

        channel = await cls.get_channel(channel_name)
        exchange = await channel.declare_exchange(cls._exchange_name, type=cls._exchange_type, auto_delete=True)
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange, routing_key=routing_key)

        try:
            consumer = Consumer(queue, func, tag)
            cls._consumers[channel_name].append(consumer)
            return consumer
        except DuplicateConsumerTag:
            raise RuntimeError(f'Duplicated consumer_tag: "{tag}"')

    @classmethod
    async def publish_event(cls, body: dict, routing_key: str, channel_name: str):
        channel = await cls.get_channel(channel_name)
        exchange = await channel.declare_exchange(
            name=cls._exchange_name,
            type=cls._exchange_type,
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
