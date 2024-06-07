import asyncio
import functools
from asyncio import Task
from typing import Callable

from loguru import logger
import ujson
from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, ExchangeType, AbstractRobustConnection
from aiormq import DuplicateConsumerTag, AMQPConnectionError

from core.repositories.routing_key import RoutingKeyRepository
from core.services.notification import RoutingKeyService
from core.utils.app_context import AppContext

from .consumer import Consumer
from .config import RabbitSettings
from .utils import RoutingKeysSet

settings = RabbitSettings()


class Eventory:
    # Connection in single per process
    _connection: AbstractRobustConnection

    # Channel per module preferred
    _channels: dict[str, AbstractChannel] = {}

    _listener_task: Task

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
    async def get_channel(cls, app_name):
        if app_name not in cls._channels:
            cls._channels[app_name] = await cls._connection.channel()
        return cls._channels[app_name]

    @classmethod
    async def remove_channel(cls, app_name):
        if app_name in cls._channels:
            await cls._channels[app_name].close()
            del cls._channels[app_name]

    @classmethod
    async def register_consumer(cls, app_name: str, routing_key: str, callback: Callable, context: AppContext, *args, **kwargs):
        """
        Consumer is message receiver, can be declared for any function
        :param app_name:
        :param routing_key:
        :param callback:
        :param args:
        :param kwargs:
        :return:
        """
        # reuse chanel for app
        channel = await cls.get_channel(app_name)

        # declare exchange for specific event
        # TODO issue possible here due to app_name not in exchange
        exchange = await channel.declare_exchange(routing_key, type=ExchangeType.FANOUT, auto_delete=True)
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange)
        try:
            receiver = cls._on_message_wrapper(callback, context, *args, **kwargs)
            consumer = Consumer(queue, receiver, callback.__name__)
            return consumer
        except DuplicateConsumerTag:
            raise RuntimeError(f'Duplicated consumer_tag: "{callback.__name__}"')

    # TODO unused function. does it suppose to be like that?
    @classmethod
    async def register_handler(cls, app_name: str, routing_keys: list[str, str], callback: Callable, *args, **kwargs):
        channel = await cls.get_channel(app_name)
        queue = await channel.declare_queue(exclusive=True)

        # bind all routing_keys
        for key, key_app_name in routing_keys:
            prefixed_routing_key = f"{key_app_name}:{key}"
            exchange = await channel.declare_exchange(
                prefixed_routing_key, type=ExchangeType.FANOUT, auto_delete=True,
            )
            await queue.bind(exchange)

        try:
            receiver = cls._on_message_wrapper(callback, *args, **kwargs)
            consumer = Consumer(queue, receiver, callback.__name__)
            return consumer
        except DuplicateConsumerTag:
            raise RuntimeError(f'Duplicated consumer_tag: "{callback.__name__}"')

    @classmethod
    async def publish(cls, obj, routing_key, app_name):
        message = Message(
            body=ujson.dumps(obj.to_dict(), ensure_ascii=False).encode('utf-8'),
            content_type='application/json',
            content_encoding='utf-8'
        )
        # TODO fix it
        prefixed_routing_key = f"{app_name}:{routing_key}"
        prefixed_routing_key = f"{routing_key}"
        channel = await cls.get_channel(app_name)
        exchange = await channel.declare_exchange(
            prefixed_routing_key,
            type=ExchangeType.FANOUT,
            auto_delete=True,
        )
        return await exchange.publish(
            message=message,
            routing_key=prefixed_routing_key,
        )

    @classmethod
    def start_listening(cls):
        cls._listener_task = asyncio.ensure_future(asyncio.Future())

    @classmethod
    def stop_listening(cls):
        if cls._listener_task:
            cls._listener_task.cancel()

    @classmethod
    def restart_listening(cls):
        cls.stop_listening()
        cls.start_listening()

    @staticmethod
    def _on_message_wrapper(coro, context, *args, **kwargs):
        @functools.wraps(coro)
        async def _receive(message: AbstractIncomingMessage):
            async with message.process():
                #logger.debug(f'Received message; consumer_tag={message.consumer_tag}  exchange={message.exchange}')

                json_data = ujson.loads(message.body.decode('utf-8'))

                # TODO needs to be fixed properly
                #message.json = json_data
                message.body = json_data
                return await coro(message=message, ctx=context, *args, **kwargs)
        return _receive

    @classmethod
    def iter_consumers(cls):
        # core consumer
        yield "core", cls._core_consumer

        # module consumers
        for app_name, module in cls._loaded_modules.items():
            for consumer in module.consumers:
                yield app_name, consumer

    @classmethod
    def get_consumer(cls, consumer_tag: str) -> tuple[str, Consumer] | tuple[None, None]:
        for app_name, consumer in cls.iter_consumers():
            if consumer.consumer_tag == consumer_tag:
                return app_name, consumer
        return None, None

    @classmethod
    async def pause_consumer(cls, consumer_tag: str) -> bool:
        app_name, consumer = cls.get_consumer(consumer_tag)
        if consumer:
            await consumer.stop()
            return True
        return False

    @classmethod
    async def resume_consumer(cls, consumer_tag: str) -> bool:
        app_name, consumer = cls.get_consumer(consumer_tag)
        if consumer:
            await consumer.start()
            return True
        return False

    @classmethod
    async def make_routing_keys_set(cls, app):
        routing_key_service = RoutingKeyService(routing_key_repo=RoutingKeyRepository())

        routing_keys = await routing_key_service.filter(app_id=app.pk)

        return RoutingKeysSet(routing_keys)
