from pydantic import BaseModel


class RedisCacheExampleSet(BaseModel):
    key: str
    value: str


class RedisCacheExampleGet(BaseModel):
    value: str


class RedisQueueExamplePush(BaseModel):
    queue_name: str
    message: dict


class RedisQueueExamplePop(BaseModel):
    message: dict
