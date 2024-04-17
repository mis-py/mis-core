from typing import Annotated

from fastapi import Request, Depends

from config import CoreSettings
from core.db.models import Module, User
from core.dependencies import get_current_user
from core.exceptions import NotFound
from core.services.base.unit_of_work import IUnitOfWork, unit_of_work_factory
from core.utils.schema import Params

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

    # module_instance = ModuleService.loaded_apps()[current_app.name]
    # TODO AppContext needed here?
    # request.state.module_proxy = module_instance.module_proxy
    # request.state.context = AppContext(
    #
    # )


UnitOfWorkDep = Annotated[IUnitOfWork, Depends(unit_of_work_factory)]
PaginateParamsDep = Annotated[Params, Depends()]
