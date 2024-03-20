from functools import lru_cache
from loguru import logger

from services.eventory import Eventory
from services.mongo.mongo import MongoService
from services.redis import RedisService
from services.scheduler import SchedulerService
from services.modules.module_service import ModuleService
from services.tortoise_manager import TortoiseManager
from services.variables.variables import VariablesManager

from config import CoreSettings

from core.routes import variable, auth, websocket, notification, team, \
    module, user, task, job, permission, guardian

from core.utils.database import setup_core, setup_admin_user, setup_guardian
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


async def init_core_routes(app):
    router = APIRouter(responses={401: {"description": "Authorization error"}}, prefix=settings.URL_ROOT_PATH)

    router.include_router(auth.router, prefix='/auth', tags=['core | auth'])
    router.include_router(user.router, prefix='/users', tags=['core | users'])
    router.include_router(team.router, prefix='/teams', tags=['core | teams'])
    router.include_router(permission.router, prefix='/permissions', tags=['core | permissions'])
    router.include_router(variable.router, prefix='/settings', tags=['core | settings'])
    # router.include_router(restricted_object.router, prefix='/restricted_objects', tags=['core | restricted_objects'])
    router.include_router(task.router, prefix='/tasks', tags=['core | tasks'])
    router.include_router(job.router, prefix='/jobs', tags=['core | jobs'])
    # router.include_router(consumer.router, prefix='/consumers', tags=['core | consumers'])
    router.include_router(module.router, prefix='/modules', tags=['core | modules'])
    router.include_router(notification.router, prefix='/notifications', tags=['core | notifications'])
    # router.include_router(log.router, prefix='/logs', tags=['core | logs'])
    router.include_router(websocket.router, prefix='/ws', tags=['core | websockets'])
    router.include_router(guardian.router, prefix='/guardian', tags=['core | guardian'])

    app.include_router(router)


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


async def init_eventory():
    await Eventory.init()
    logger.success('Eventory started')


async def shutdown_eventory():
    await Eventory.close()
    logger.info('Eventory shutdown')


async def init_core():
    initialized = await setup_core()
    if initialized:
        logger.success('Core and permissions initialized')
    else:
        logger.info('Core already initialized')


async def init_admin_user():
    initialized = await setup_admin_user()
    if initialized:
        logger.success('Admin user and team initialized')
    else:
        logger.info('Admin user and team already initialized')


async def init_guardian():
    await setup_guardian()
    logger.info('Guardian initialized')


async def init_scheduler():
    await SchedulerService.init()
    logger.success('Scheduler started')


async def shutdown_scheduler():
    await SchedulerService.close()
    logger.info('SchedulerService shutdown')


async def init_redis():
    await RedisService.init()
    logger.success('RedisService started')


async def shutdown_redis():
    await RedisService.close()
    logger.info('RedisService shutdown')


async def init_mongo():
    await MongoService.init()
    logger.success('MongoService started')


async def shutdown_mongo():
    await MongoService.close()
    logger.info('MongoService shutdown')


async def manifest_init_modules(app):
    await ModuleService.manifest_init(app)
    logger.success('Modules manifest initialized')


async def pre_init_modules(app):
    await ModuleService.pre_init(app)
    logger.success('Modules pre initialized')


async def init_modules(app):
    await ModuleService.init(app)
    logger.success('Modules initialized')


async def shutdown_modules():
    await ModuleService.shutdown()
    logger.info("Modules shutdown complete")


async def init_settings():
    await VariablesManager.init()
    logger.info('Settings loaded!')
