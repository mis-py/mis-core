from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_URI: str = "redis://mis-redis"
