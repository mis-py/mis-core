from typing import Annotated

import loguru
from fastapi import Request, Depends

from config import CoreSettings
from core.db.models import Module, User
from core.dependencies.security import get_current_user
from core.exceptions import NotFound
from core.utils.schema import Params
from services.eventory import Eventory
from services.eventory.utils import RoutingKeysSet
from services.modules.context import AppContext
from services.modules.module_service import ModuleService
from services.variables.variables import VariablesManager

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


async def inject_user(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    request.state.current_user = current_user


async def inject_context(
        request: Request,
        current_app: Module = Depends(get_current_app)
):
    request.state.current_app = current_app


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


AppContextDep = Annotated[AppContext, Depends(get_app_context)]

PaginateParamsDep = Annotated[Params, Depends()]

RoutingKeysDep = Annotated[RoutingKeysSet, Depends(get_routing_keys)]
