from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import MongoSettings

settings = MongoSettings()


class MongoService:
    client: AsyncIOMotorClient
    database: AsyncIOMotorDatabase

    @classmethod
    async def init(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        cls.database = cls.client.get_database(settings.MONGODB_TABLE)

    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
