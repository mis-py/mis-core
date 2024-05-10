from typing import Annotated

import tortoise.exceptions
from fastapi import APIRouter, Security, Depends
from fastapi import Request
from loguru import logger

from core.db.models import Module

from core.dependencies.security import get_current_user
from core.dependencies.misc import  PaginateParamsDep
from core.dependencies.services import get_module_service
from core.dependencies.path import get_module_by_id
from core.schemas.module import ModuleManifestResponse
from core.services import module
from core.utils.schema import PageResponse, MisResponse
# from .schema import BundleAppModel

from services.modules.exceptions import LoadModuleError, StartModuleError
from services.modules.module_service import ModuleService

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user)],
    response_model=PageResponse[ModuleManifestResponse]
)
async def get_modules(
        module_service: Annotated[module.ModuleService, Depends(get_module_service)],
        paginate_params: PaginateParamsDep, module_id: int = None
):
    if module_id:
        await module_service.get_or_raise(id=module_id)

    paginated_modules = await module_service.filter_and_paginate(
        id=module_id, params=paginate_params
    )
    modules_with_manifest = await module_service.set_manifest_in_response(paginated_modules)
    return modules_with_manifest


@router.post(
    '/init',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse[ModuleManifestResponse]
)
async def init_module(
        module_service: Annotated[module.ModuleService, Depends(get_module_service)],
        request: Request,
        module: Module = Depends(get_module_by_id),
):
    inited_module = await ModuleService.init_module(request.app, module.name)

    module_response = ModuleManifestResponse(
        id=inited_module.get_id(),
        name=inited_module.name,
        enabled=inited_module.is_enabled(),
        state=inited_module.get_state(),
        manifest=module_service.get_manifest(inited_module.name)
    )

    return MisResponse[ModuleManifestResponse](result=module_response)


@router.post(
    '/start',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse[ModuleManifestResponse]
)
async def start_module(
        module_service: Annotated[module.ModuleService, Depends(get_module_service)],
        module: Module = Depends(get_module_by_id),
):
    started_module = await ModuleService.start_module(module.name)

    module_response = ModuleManifestResponse(
        id=started_module.get_id(),
        name=started_module.name,
        enabled=started_module.is_enabled(),
        state=started_module.get_state(),
        manifest=module_service.get_manifest(started_module.name)
    )

    return MisResponse[ModuleManifestResponse](result=module_response)


@router.post(
    '/stop',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse[ModuleManifestResponse]
)
async def stop_module(
        module_service: Annotated[module.ModuleService, Depends(get_module_service)],
        module: Module = Depends(get_module_by_id)
):
    stopped_module = await ModuleService.stop_module(module.name)

    module_response = ModuleManifestResponse(
        id=stopped_module.get_id(),
        name=stopped_module.name,
        enabled=stopped_module.is_enabled(),
        state=stopped_module.get_state(),
        manifest=module_service.get_manifest(stopped_module.name)
    )

    return MisResponse[ModuleManifestResponse](result=module_response)


@router.post(
    '/shutdown',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse()
)
async def shutdown_application(
        module_service: Annotated[module.ModuleService, Depends(get_module_service)],
        module: Module = Depends(get_module_by_id),
):
    await ModuleService.shutdown_module(module.name)

    return MisResponse()


# @router.get(
#     '/loaded_modules',
#     dependencies=[Security(get_current_active_user, scopes=['core:sudo'])]
# )
# async def get_loaded_modules(request: Request):
#     app_models = await BundleAppModel.from_queryset(App.all())
#     loaded_modules = request.app.module_loader.loaded_apps
#
#     response = []
#     for app in app_models:
#         if app.name == 'core':
#             continue
#         if app.name not in loaded_apps:
#             continue
#
#         response.append({'id': app.id, 'enabled': app.enabled, **loaded_apps[app.name].get_info_dict()})
#
#     # apps = [value.get_info_dict() for value in loaded_apps.values()]
#
#     return JSONResponse(content=response, media_type='application/json')


# @router.get(
#     '/get',
#     dependencies=[Security(get_current_user)],
#     response_model=AppModel,
# )
# async def get_module_info():
#     return await AppModel.from_tortoise_orm(app)


# @router.get(
#     '/{app_name}',
#     dependencies=[Security(get_current_active_user)],
# )
# async def get_app_file(app_name: str):
# try:
#     with open(FRONTEND_DIR / app_name / 'index.html') as data:
#         return Response(content=data.read(), media_type='text/html')
# except FileNotFoundError as error:
#     raise CoreError(str(error))
# pass


# @router.get(
#     '/{app_name}/{file:path}',
#     dependencies=[Security(get_current_active_user)]
# )
# async def get_app_file_path(app_name: str, file: str):
# path = FRONTEND_DIR / app_name / file
# with open(path) as data:
#     media_type, encoding = guess_type(path)
#     return Response(content=data.read(), media_type=media_type)
# pass

# @router.post(
#     '/install',
#     dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
#     response_model=AppModel
# )
# async def install_module(name: str, request: Request):
#     if name not in os.listdir(BASE_DIR / 'modules'):
#         raise InstallModuleError("App is not loaded into modules directory")
#
#     # app, is_created = await crud_app.get_or_create(name=name)
#     await ModuleService.init_module(request.app, name)
#     return 'ok'

# @router.post(
#     '/install',
#     dependencies=[Security(get_current_active_user, scopes=['core:sudo'])],
#     response_model=AppModel
# )
# async def install_application(app_data: DownloadAppInput, request: Request):
#     app_name = request.app.module_loader.download_app(**app_data.dict())
#
#     app, is_created = await crud.app.get_or_create(name=app_name)
#     await request.app.module_loader.load_app(app, is_created)
#     return app