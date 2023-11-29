from functools import lru_cache
from loguru import logger
import os

from services.eventory import Eventory
from services.mongo.mongo import MongoService
from services.redis import RedisService
from services.scheduler import SchedulerService
from services.modules.module_service import ModuleService
from services.notifications import notifications
from services.tortoise_manager import TortoiseManager

from const import DEFAULT_ADMIN_USERNAME
from config import CoreSettings
from core.db import User, Permission, Setting, Team, App
from core.security.utils import get_password_hash
from core.routes.access_groups import access_groups
from core.routes.auth import auth
from core.routes.users import users
from core.routes.permissions import permissions
from core.routes.teams import teams
from core.routes.variables import settings as variables
from core.routes.consumers import consumers
from core.routes.restricted_objects import restricted_objects
from core.routes.modules import modules
from core.routes.logs import logs
from core.routes.websocket import websocket
from core.routes.tasks import task_router, jobs_router

# from modules.core.websockets.actions import Action, send_log_to_subscribers, send_notification_to_subscribers
# from modules.core.websockets.manager import WSManager, ws_manager
# from fastapi.openapi.docs import get_swagger_ui_html
# from types import ModuleType
# from typing import Dict, Iterable, Optional, Union

from fastapi import APIRouter
# from pydantic import BaseModel  # pylint: disable=E0611


@lru_cache
def get_settings():
    return CoreSettings()


settings = get_settings()


# class MISApp(FastAPI):
    # def regen_openapi(self):
    #     self.openapi_schema = None
    #     self.setup()
    #
    # async def swagger_ui_html(self, req: Request):
    #     root_path = req.scope.get("root_path", "").rstrip("/")
    #     openapi_url = root_path + self.openapi_url
    #     logging.debug(openapi_url)
    #     oauth2_redirect_url = self.swagger_ui_oauth2_redirect_url
    #     if oauth2_redirect_url:
    #         oauth2_redirect_url = root_path + oauth2_redirect_url
    #     return get_swagger_ui_html(
    #         openapi_url=openapi_url,
    #         title=self.title + " - Swagger UI",
    #         oauth2_redirect_url=oauth2_redirect_url,
    #         init_oauth=self.swagger_ui_init_oauth,
    #         swagger_ui_parameters=self.swagger_ui_parameters,
    #     )

    # async def init_app(self):
    #     pass
        # async def openapi(req: Request) -> JSONResponse:
        #     return JSONResponse(self.openapi())
        #
        # if core_settings.ENVIRONMENT != PROD_ENVIRONMENT:
        #     self.add_route('/api/openapi.json', openapi, include_in_schema=False)


async def init_core_routes(app):
    router = APIRouter(responses={401: {"description": "Authorization error"}}, prefix=settings.URL_ROOT_PATH)

    router.include_router(auth.router, prefix='/auth', tags=['core | auth'])
    router.include_router(users.router, prefix='/users', tags=['core | users'])
    router.include_router(teams.router, prefix='/teams', tags=['core | teams'])
    router.include_router(access_groups.router, prefix='/groups', tags=['core | groups'])
    router.include_router(permissions.router, prefix='/permissions', tags=['core | permissions'])
    router.include_router(variables.router, prefix='/settings', tags=['core | settings'])
    router.include_router(restricted_objects.router, prefix='/restricted_objects', tags=['core | restricted_objects'])
    router.include_router(task_router, prefix='/tasks', tags=['core | tasks'])
    router.include_router(jobs_router, prefix='/jobs', tags=['core | jobs'])
    router.include_router(consumers.router, prefix='/consumers', tags=['core | consumers'])
    router.include_router(modules.router, prefix='/modules', tags=['core | modules'])
    router.include_router(notifications.router, prefix='/notifications', tags=['core | notifications'])
    router.include_router(logs.router, prefix='/logs', tags=['core | logs'])
    router.include_router(websocket.router, prefix='/ws', tags=['core | websockets'])

    app.include_router(router)

    # for route in self.router.routes:
    # logging.debug(route)


async def pre_init_db():
    await TortoiseManager.pre_init()


async def init_db(app, generate_schemas=True, add_exception_handlers=True):
    await TortoiseManager.init(app, generate_schemas, add_exception_handlers)
    logger.success("Tortoise-ORM started")  # , {}, {}", connections._get_storage(), Tortoise.apps)


async def shutdown_db():
    await TortoiseManager.shutdown()
    logger.info("Tortoise-ORM shutdown")


async def init_migrations():
    await TortoiseManager.init_migrations()
    logger.success('Migrations applied!')


async def init_eventory(app):
    await Eventory.init()
    logger.success('Eventory started')


async def shutdown_eventory():
    await Eventory.close()
    logger.info('Eventory shutdown')


async def init_core():
    core = await App.get_or_none(name='core')
    if core is None:
        core = await App.create(name='core')
        await Permission.create(name='Superuser permissions', scope='sudo', app=core)
        await Permission.create(name="Access for 'users' endpoints", scope="users", app=core)
        await Permission.create(name="Access for 'teams' endpoints", scope="teams", app=core)
        await Permission.create(name="Access for 'modules' endpoints", scope="modules", app=core)
        await Permission.create(name="Access for 'groups' endpoints", scope="groups", app=core)
        await Permission.create(name="Access for 'notifications' endpoints", scope="notifications", app=core)
        await Permission.create(name="Access for 'logs' endpoints", scope="logs", app=core)
        await Permission.create(name="Access for 'tasks' endpoints", scope="tasks", app=core)
        await Permission.create(name="Access for 'consumers' endpoints", scope="consumers", app=core)
        await Permission.create(name="Access for 'modules' endpoints", scope="modules", app=core)
        await Permission.create(name="Access for 'permissions' endpoints", scope="permissions", app=core)

        logger.success('Core and permissions initialized')
    else:
        logger.info('Core already initialized')


async def init_admin_user():
    if not await User.get_or_none(username=DEFAULT_ADMIN_USERNAME):
        team = await Team.create(name='Superusers')
        user = await User.create(
            username=DEFAULT_ADMIN_USERNAME,
            team=team,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)
        )

        await user.set_permissions(['core:sudo'])
        await team.set_permissions(['core:sudo'])

        logger.success('Admin user and team initialized')
    else:
        logger.info('Admin user and team already initialized')


async def init_scheduler(app):
    await SchedulerService.init()
    logger.success('Scheduler started')


async def shutdown_scheduler():
    await SchedulerService.close()
    logger.info('SchedulerService shutdown')


async def init_redis(app):
    await RedisService.init()
    logger.success('RedisService started')


async def shutdown_redis():
    await RedisService.close()
    logger.info('RedisService shutdown')


async def init_mongo(app):
    await MongoService.init()
    logger.success('MongoService started')


async def shutdown_mongo():
    await MongoService.close()
    logger.info('MongoService shutdown')


async def pre_init_modules(app):
    await ModuleService.pre_init(app)
    logger.success('Modules pre initialized')


async def init_modules(app):
    await ModuleService.init(app)
    await ModuleService.start_app('dummy')
    logger.success('Modules initialized')


async def shutdown_modules():
    await ModuleService.shutdown()
    logger.info("Modules shutdown complete")


async def init_settings():
    async for setting in Setting.filter(default_value__isnull=False):
        logger.debug(f' - setting {setting.key} -> {setting.default_value}')
        os.environ.setdefault(setting.key, setting.default_value)

    logger.info('Settings loaded!')
