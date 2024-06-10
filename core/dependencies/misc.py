from typing import Annotated

from fastapi import Request, Depends

from config import CoreSettings
from core.db.models import Module, User
from core.dependencies.security import get_current_user
from core.dependencies.routing_key_service import get_routing_key_service
from core.exceptions import NotFound
from core.utils.schema import Params
from libs.eventory.utils import RoutingKeysSet
from libs.redis import RedisService

settings = CoreSettings()


async def get_current_app(request: Request):
    path = request.url.components.path.replace(settings.ROOT_PATH, '')
    path_array = path.split('/')
    path_array = list(filter(len, path_array))
    name = path_array[0]
    app = await Module.get_or_none(name=name)
    if not app:
        raise NotFound('AppModel is not found in DB')
    return app


# TODO move it to correspongins libs deps
async def get_routing_keys(
        module=Depends(get_current_app),
        routing_key_service=Depends(get_routing_key_service)
):
    return await routing_key_service.make_routing_keys_set(module=module)


async def get_redis_service() -> RedisService:
    return RedisService()


PaginateParamsDep = Annotated[Params, Depends()]

RoutingKeysDep = Annotated[RoutingKeysSet, Depends(get_routing_keys)]

RedisServiceDep = Annotated[RedisService, Depends(get_redis_service)]
