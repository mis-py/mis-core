from aio_pika.queue import Queue
from typing import Literal
from loguru import logger


class Consumer:
    def __init__(self, queue, receiver, consumer_tag):
        self.queue: Queue = queue
        self.receiver = receiver
        self.consumer_tag = consumer_tag
        self.status: Literal["running", "paused"] = "running"

    async def start(self):
        await self.queue.consume(self.receiver, consumer_tag=self.consumer_tag)
        self.status = "running"

    async def stop(self):
        await self.queue.cancel(self.consumer_tag, timeout=5)
        self.status = "paused"
        # try:
        #     pass
            # loguru.logger.debug(self.queue.channel.consumers)
            # self.queue.channel.consumers.pop(self.consumer_tag)
        # except KeyError as e:
        #     logger.error(f'KeyError: {e}')

    def __str__(self):
        return f'<Consumer: {self.consumer_tag}>'

    def __repr__(self):
        return self.__str__()
