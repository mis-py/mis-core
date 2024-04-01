import tortoise.exceptions
from fastapi import APIRouter, Security, Depends
from fastapi import Response, Request
from fastapi_pagination import Page
from loguru import logger

from core.db.models import Module

from core.dependencies import get_current_user
from core.dependencies.misc import UnitOfWorkDep, PaginateParamsDep
from core.dependencies.path import get_module_by_id
from core.schemas.module import ModuleManifestResponse
from core.services.module import ModuleUOWService

# from .schema import BundleAppModel

from services.modules.exceptions import LoadModuleError, StartModuleError
from services.modules.module_service import ModuleService

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user)],
    response_model=Page[ModuleManifestResponse]
)
async def get_modules(uow: UnitOfWorkDep, paginate_params: PaginateParamsDep, module_id: int = None):
    paginated_modules = await ModuleUOWService(uow).filter_and_paginate(
        app_id=module_id, params=paginate_params
    )
    modules_with_manifest = await ModuleUOWService(uow).set_matifest_in_response(paginated_modules)
    return modules_with_manifest


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


@router.put(
    '/init',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])]
)
async def init_module(
        uow: UnitOfWorkDep,
        request: Request,
        module: Module = Depends(get_module_by_id),
):
    module_uow_service = ModuleUOWService(uow)
    try:
        if module.enabled:
            await ModuleService.stop_module(module.name, module_uow_service)

        await ModuleService.init_module(module.name, request.app, module_uow_service)
    except ModuleNotFoundError as e:
        logger.exception(e)
        raise LoadModuleError(
            "App name is wrong, or app is not loaded into 'modules' directory")
    except tortoise.exceptions.ConfigurationError as e:
        raise LoadModuleError(
            f"Loaded app have wrong configuration. Details: {' '.join(e.args)}")
    except Exception as e:
        logger.exception(e)
        raise LoadModuleError(f"Error while loading app. Details: {str(e)}")

    return Response(status_code=200)


@router.put(
    '/shutdown',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])]
)
async def shutdown_application(
        uow: UnitOfWorkDep,
        module: Module = Depends(get_module_by_id),
):
    module_uow_service = ModuleUOWService(uow)
    await ModuleService.shutdown_module(module.name, module_uow_service)
    return Response(status_code=200)


@router.put(
    '/start',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])]
)
async def start_module(
        uow: UnitOfWorkDep,
        module: Module = Depends(get_module_by_id),
):
    module_uow_service = ModuleUOWService(uow)
    try:
        await ModuleService.start_module(module.name, module_uow_service)
    except Exception as e:
        logger.exception(e)
        raise StartModuleError(f"Error while starting app. Details: {str(e)}")
    return Response(status_code=200)


@router.put(
    '/stop',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])]
)
async def stop_module(
        uow: UnitOfWorkDep,
        module: Module = Depends(get_module_by_id)
):
    module_uow_service = ModuleUOWService(uow)
    await ModuleService.stop_module(module.name, module_uow_service)
    return True

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