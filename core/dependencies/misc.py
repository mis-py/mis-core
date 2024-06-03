from typing import Annotated

from fastapi import Request, Depends

from config import CoreSettings
from core.db.models import Module, User
from core.dependencies.security import get_current_user
from core.exceptions import NotFound
from core.utils.schema import Params
from libs.eventory import Eventory
from libs.eventory.utils import RoutingKeysSet
from libs.modules.AppContext import AppContext
from libs.modules.module_service import ModuleService
from libs.redis import RedisService

settings = CoreSettings()


async def get_current_app(request: Request):
    path = request.url.components.path.replace(settings.URL_ROOT_PATH, '')
    path_array = path.split('/')
    path_array = list(filter(len, path_array))
    name = path_array[0]
    app = await Module.get_or_none(name=name)
    if not app:
        raise NotFound('AppModel is not found in DB')
    return app


# TODO move it to correspongins libs deps
async def get_routing_keys(
        module=Depends(get_current_app)
):
    return await Eventory.make_routing_keys_set(app=module)


async def get_app_context(
        user: User = Depends(get_current_user),
        module: Module = Depends(get_current_app)
):
    await user.fetch_related('team')
    return await ModuleService.make_module_context(module_name=module.name, user=user, team=user.team)


async def get_userless_app_context(
        module: Module = Depends(get_current_app)
):
    return await ModuleService.make_module_context(module_name=module.name)


async def get_redis_service() -> RedisService:
    return RedisService()


AppContextDep = Annotated[AppContext, Depends(get_app_context)]

UserlessAppContextDep = Annotated[AppContext, Depends(get_userless_app_context)]

PaginateParamsDep = Annotated[Params, Depends()]

RoutingKeysDep = Annotated[RoutingKeysSet, Depends(get_routing_keys)]

RedisServiceDep = Annotated[RedisService, Depends(get_redis_service)]
