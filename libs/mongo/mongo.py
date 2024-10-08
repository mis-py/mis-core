from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import MongoSettings

settings = MongoSettings()


class MongoService:
    _db_url = (
        f"mongodb://{settings.MONGO_INITDB_ROOT_USERNAME}:{settings.MONGO_INITDB_ROOT_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/"
    )

    client: AsyncIOMotorClient
    database: AsyncIOMotorDatabase

    @classmethod
    async def init(cls):
        cls.client = AsyncIOMotorClient(cls._db_url)
        cls.database = cls.client.get_database(settings.MONGO_INITDB_DATABASE)

    @classmethod
    async def close(cls):
        if cls.client is not None:
            cls.client.close()
