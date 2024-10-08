from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_HOST: str = "mis-redis"
