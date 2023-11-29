import json
from datetime import timedelta

from redis import asyncio as aioredis
from .config import RedisSettings

settings = RedisSettings()


class RedisQueue:
    def __init__(self, client: aioredis.Redis):
        self.client = client

    async def push(self, queue_name, message_dict):
        message_json = json.dumps(message_dict)
        await self.client.rpush(queue_name, message_json)

    async def pop(self, queue_name):
        message_json = await self.client.lpop(queue_name)
        if message_json:
            message_dict = json.loads(message_json)
            return message_dict
        return None


class RedisCache:
    def __init__(self, client: aioredis.Redis):
        self.client = client

    @staticmethod
    def _make_key(cache_name: str, key: str) -> str:
        return f"{cache_name}:{key}"

    async def get(self, cache_name: str, key: str):
        cache_key = self._make_key(cache_name, key)
        return await self.client.get(name=cache_key)

    async def set(self, cache_name: str, key: str, value: str):
        cache_key = self._make_key(cache_name, key)
        await self.client.set(
            name=cache_key,
            value=value,
        )

    async def setex(self, cache_name: str, key: str, value: str, time: timedelta = timedelta(minutes=3600)):
        cache_key = self._make_key(cache_name, key)
        await self.client.setex(
            name=cache_key,
            value=value,
            time=time,
        )

    async def get_json(self, cache_name: str, key: str) -> dict:
        value = await self.get(cache_name=cache_name, key=key)
        if value is None:
            return {}
        return json.loads(value)

    async def set_json(self, cache_name: str, key: str, value: dict) -> None:
        await self.set(
            cache_name=cache_name,
            key=key,
            value=json.dumps(value),
        )

    # *ex means time expiration
    async def setex_json(self, cache_name: str, key: str, value: dict, time: timedelta = timedelta(minutes=3600)):
        await self.setex(
            cache_name=cache_name,
            key=key,
            value=json.dumps(value),
            time=time,
        )


class RedisService:
    client: aioredis.Redis

    # queue is for storing data sequences
    queue: RedisQueue

    # cache for storing some temp data in redis
    cache: RedisCache

    @classmethod
    async def init(cls):
        cls.client = aioredis.from_url("redis://" + settings.REDIS_HOST, decode_responses=True)

        if not cls.client:
            raise Exception("Please connect, before init services")

        cls.queue = RedisQueue(cls.client)

        cls.cache = RedisCache(cls.client)

    @classmethod
    async def close(cls):
        if cls.client is not None:
            await cls.client.close()

    @classmethod
    async def scan(cls, match):
        cursor, keys = await cls.client.scan(match=match)
        return cursor, keys

    @classmethod
    async def mget(cls, keys: list):
        values = await cls.client.mget(keys)
        return values
