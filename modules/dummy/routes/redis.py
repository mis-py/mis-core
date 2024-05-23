from fastapi import APIRouter, Depends
from starlette import status

from core.db.models import User
from core.dependencies.misc import RedisServiceDep
from core.dependencies.security import get_current_user
from core.exceptions import NotFound
from core.utils.schema import MisResponse
from modules.dummy.schemas.redis import RedisCacheExampleSet, RedisCacheExampleGet, RedisQueueExamplePush, \
    RedisQueueExamplePop

router = APIRouter()


@router.post(
    "/cache/set",
    response_model=MisResponse,
)
async def set_cache(
        redis_service: RedisServiceDep,
        schema_in: RedisCacheExampleSet,
        user: User = Depends(get_current_user),
):
    await redis_service.cache.set(cache_name=user.username, key=schema_in.key, value=schema_in.value)
    return MisResponse(status_code=status.HTTP_201_CREATED)


@router.get(
    "/cache/get",
    response_model=MisResponse[RedisCacheExampleGet]
)
async def get_cache(
        redis_service: RedisServiceDep,
        key: str,
        user: User = Depends(get_current_user),
):
    value = await redis_service.cache.get(cache_name=user.username, key=key)
    if not value:
        raise NotFound(f"Cache key '{key}' not found")
    return MisResponse[RedisCacheExampleGet](result={'value': value})


@router.post(
    "/queue/push",
    response_model=MisResponse,
)
async def queue_push(
        redis_service: RedisServiceDep,
        schema_in: RedisQueueExamplePush
):
    await redis_service.queue.push(queue_name=schema_in.queue_name, message_dict=schema_in.message)
    return MisResponse(status_code=status.HTTP_201_CREATED)


@router.get(
    "/queue/pop",
    response_model=MisResponse[RedisQueueExamplePop]
)
async def queue_pop(
        redis_service: RedisServiceDep,
        queue_name: str
):
    message = await redis_service.queue.pop(queue_name=queue_name)
    if not message:
        raise NotFound("Queue is empty")
    return MisResponse[RedisQueueExamplePop](result={'message': message})
