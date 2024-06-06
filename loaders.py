from loguru import logger

from libs.eventory import Eventory
from libs.mongo.mongo import MongoService
from libs.redis import RedisService
from libs.schedulery import Schedulery
from libs.modules.module_service import Modulery
from libs.tortoise_manager import TortoiseManager

from config import CoreSettings

from core.routes import variable, auth, websocket, notification, team, \
    module, user, task, job, permission, guardian

from core.utils.core_setup import setup_core, setup_admin_user, setup_guardian
# from modules.core.websockets.actions import Action, send_log_to_subscribers, send_notification_to_subscribers
# from modules.core.websockets.manager import WSManager, ws_manager
# from fastapi.openapi.docs import get_swagger_ui_html
# from types import ModuleType
# from typing import Dict, Iterable, Optional, Union

from fastapi import APIRouter


settings = CoreSettings()


async def init_core_routes(app):
    router = APIRouter(responses={401: {"description": "Authorization error"}})

    router.include_router(auth.router, prefix='/auth', tags=['core | auth'])
    router.include_router(user.router, prefix='/users', tags=['core | users'])
    router.include_router(team.router, prefix='/teams', tags=['core | teams'])
    router.include_router(permission.router, prefix='/permissions', tags=['core | permissions'])
    router.include_router(variable.router, prefix='/variables', tags=['core | variables'])
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
    logger.success("Tortoise-ORM pre-init finished")


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
    logger.success('Guardian initialized')


async def init_scheduler():
    await Schedulery.init()
    logger.success('Scheduler started')


async def shutdown_scheduler():
    await Schedulery.close()
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


async def manifest_init_modules():
    await Modulery.manifest_init()
    logger.success('Modules manifest initialized')


async def pre_init_modules(application):
    await Modulery.pre_init(application)
    logger.success('Modules pre initialized')


async def init_modules():
    await Modulery.init()
    logger.success('Modules initialized')


async def shutdown_modules():
    await Modulery.shutdown()
    logger.info("Modules shutdown complete")


async def init_settings():
    # why should we load settings to env? it's not secure at all
    # await VariablesManager.init()
    # logger.info('Settings loaded!')
    raise Exception("Do not use me pls")


async def init_modules_root_model():
    # await Modulery.init_modules_root_model()
    # logger.success('Modules root model initialized')
    logger.error('Modules models not initialized!!')