import itertools
import re
from asyncio import Task
from typing import Literal

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import Depends
from fastapi.routing import APIRoute, APIRouter
from loguru import logger
from tortoise.exceptions import DoesNotExist, IntegrityError
from aiormq import DuplicateConsumerTag

# from core.db import ScheduledJob
# from core.utils import validate_task_extra
from core.crud import job

from config import CoreSettings
from const import DEFAULT_ADMIN_USERNAME, PROD_ENVIRONMENT, ENVIRONMENT, LOGS_DIR, MODULES_DIR
from core.db.models import ScheduledJob
from core.dependencies.misc import inject_context, inject_user
from core.crud import user, permission, variables
from core.utils.common import pydatic_model_to_dict, signature_to_dict
from services.modules.context import AppContext

from services.scheduler.scheduler import SchedulerService
from services.scheduler.utils import Task
from services.eventory.eventory import Eventory
from services.eventory.consumer import Consumer
from services.eventory.utils import EventTemplate
# from services.modules.context import AppContext
from core.crud.notification import routing_key
from services.tortoise_manager import TortoiseManager
from services.modules.component import Component


core_settings = CoreSettings()


class TortoiseModels(Component):

    async def pre_init(self):
        logger.debug(f"[{self.module.name}] Initialising models")

        await TortoiseManager.add_models(self.module.name, [f'modules.{self.module.name}.db.models'])
        await TortoiseManager.add_migrations(str(MODULES_DIR / self.module.name / "migrations"))

    async def init(self, application, app_db_model, is_created: bool):
        pass

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass


class EventManager(Component):
    def __init__(self):
        self.events: list[EventTemplate] = []
        self.consumers: list[Consumer] = []

    def add_consumer(self, route_key):
        def _wrapper(func):
            self.events.append(EventTemplate(func, route_key))
            return func
        return _wrapper

    async def pre_init(self):
        pass

    async def init(self, application, app_db_model, is_created: bool):
        for template in self.events:
            logger.debug(f'[EventManager]: Register consumer {template.func.__name__} from {self.module.name}')

            # consumers has only app context coz no user or team is running consumer
            context = await self.module.get_context()

            consumer = await Eventory.register_consumer(
                app_name=self.module.name,
                routing_key=template.route_key,
                callback=template.func,
                app_context=context
            )
            self.consumers.append(consumer)

        logger.debug(f"[EventManager] Consumers added for {self.module.name}")

    async def start(self):
        for consumer in self.consumers:
            logger.debug(f'[EventManager] Starting consumer {consumer.consumer_tag} from {self.module.name}')
            try:
                await consumer.start()
            except DuplicateConsumerTag as e:
                logger.error(f"Consumer already exists: {e}")

        # TODO should I restart it actually?
        # Eventory.restart_listening()

    async def stop(self):
        for consumer in self.consumers:
            logger.debug(f'[EventManager] Stopping consumer {consumer.consumer_tag} from {self.module.name}')
            await consumer.stop()
        await Eventory.remove_channel(self.module.name)

    async def shutdown(self):
        await self.stop()
        self.consumers.clear()


class ScheduledTasks(Component):
    def __init__(self):
        # list of all declared tasks on init
        self.tasks: list[Task] = []

    def schedule_task(self, task_type: Literal['user', 'team'] = 'user', autostart: bool = False,  *args, **kwargs):
        """
        Use it as wrapper to schedule tasks
        :param autostart:
        :param task_type:
        :param args:
        :param kwargs:
        :return:
        """
        if 'trigger' in kwargs and (isinstance(kwargs['trigger'], BaseTrigger) or kwargs['trigger'] is None):
            trigger = kwargs['trigger']
        elif any(arg in kwargs for arg in ('seconds', 'hours', 'minutes')):
            trigger = IntervalTrigger(**kwargs)
        elif (arg in kwargs for arg in ('second', 'hour', 'minute')):
            trigger = CronTrigger(**kwargs, )
        else:
            raise ValueError(f"scheduled task got invalid kwargs: {kwargs}")

        def _wrapper(func):
            extra_typed = signature_to_dict(func)
            extra_typed.pop("ctx", False)
            self.tasks.append(Task(
                type=task_type,
                func=func,
                trigger=trigger,
                extra_typed=extra_typed,
                autostart=autostart
            ))
            return func
        return _wrapper

    async def pre_init(self):
        pass

    async def init(self, application, app_db_model, is_created: bool):
        logger.debug(f"[{self.module.name}] Adding scheduled tasks")

        # register in SchedulerService all declared tasks
        for task in self.tasks:
            SchedulerService.add_task(task, self.module)

        logger.debug(f"[{self.module.name}] Added scheduled tasks ")

    async def start(self):
        """
        Restore running tasks that saved in DB
        :return:
        """
        saved_scheduled_jobs = await job.get_all_scheduled_jobs(self.module.name)
        for saved_job in saved_scheduled_jobs:
            await SchedulerService.restore_job(
                saved_job=saved_job,
                module=self.module,
                run_at_startup=saved_job.status == ScheduledJob.StatusTask.RUNNING
            )

        # TODO implement autostart at root user

    async def stop(self):
        pass
        # TODO actually it set pause for all jobs in db
        # jobs = await crud_jobs.get_all_scheduled_jobs(self.module.name)
        # for job in jobs:
        #     logger.debug(f'[{self.module.name}]: Pause job {job.name}')
        #     job.pause()
        # await crud_jobs.set_pause_all_app_jobs(self.module.name)

    async def shutdown(self):
        pass
        # TODO actually it removes all saved jobs from db
        # for job in self.module.jobs:
        #     logger.debug(f'{self.module.name}[JOB]: Remove job {job.name}')
        #     job.remove()
        # await crud_jobs.remove_all_app_tasks(self.module.name)


class APIRoutes(Component):
    def __init__(self, router: APIRouter):
        self.router: APIRouter = router
        self.application = None

    async def pre_init(self):
        pass

    async def init(self, application, app_db_model, is_created: bool):
        self.application = application

    async def start(self):
        dependencies = [Depends(inject_context)]
        if not self.module.auth_disabled:
            dependencies.append(Depends(inject_user))

        for route in self.router.routes:
            if route.tags:
                tags = [f'{self.module.name} | {route.tags[0]}']
            else:
                tags = [self.module.name]
            route.tags = tags

        self.application.include_router(
            self.router,
            prefix=f"{core_settings.URL_ROOT_PATH}/{self.module.name}",
            dependencies=dependencies,
        )

        await self.regen_openapi()

    async def stop(self):
        for route in filter(lambda r: isinstance(r, APIRoute), self.application.router.routes):
            if self.module.name in route.tags:
                self.application.router.routes.remove(route)
        await self.regen_openapi()

    async def shutdown(self):
        await self.stop()

    async def regen_openapi(self):
        self.application.openapi_schema = None
        self.application.setup()


class Variables(Component):
    def __init__(self, module_settings, user_settings):
        self.module_settings = module_settings
        self.user_settings = user_settings

    async def pre_init(self):
        pass

    async def init(self, application, app_db_model, is_created: bool):
        logger.debug(f'[Variables] Connecting variables for {self.module.name}')

        await self.save_permissions(app_db_model)
        await self.save_variables(app_db_model)

        logger.debug(f'[Variables] Variables connected for {self.module.name}')

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass

    async def save_permissions(self, app_model):
        # TODO somewhy user not exist here?
        # admin_user = await user.get(username=DEFAULT_ADMIN_USERNAME)

        exist_permission_ids = []
        for scope, description in self.module.permissions.items():
            perm = await permission.update_or_create(
                app=app_model,
                name=description,
                scope=scope,
            )
            logger.debug(f'[Variables] Created permission {scope} for {self.module.name}')

            #await admin_user.add_permission(f'{app_model.name}:{scope}')
            exist_permission_ids.append(perm.id)

        logger.debug(f'[Variables] Permissions saved for {self.module.name}')

        deleted_count = await permission.remove_unused(app=app_model, exist_ids=exist_permission_ids)
        logger.debug(f'[Variables] Deleted {deleted_count} unused permissions for {self.module.name}')

    async def save_variables(self, app_model):
        app_settings, user_settings = dict(self.module_settings), dict(self.user_settings)
        settings = itertools.chain(app_settings.items(), user_settings.items())

        typed_settings = {
            **pydatic_model_to_dict(self.user_settings),
            **pydatic_model_to_dict(self.module_settings),
        }

        for key, default_value in settings:
            setting_type = typed_settings[key]["type"]
            is_global = key in app_settings
            setting, is_created = await variables.get_or_create(
                app=app_model,
                key=key,
                default_value=default_value,
                is_global=is_global,
                type=setting_type
            )
            if not is_created:
                await variables.update_params(
                    variable=setting,
                    default_value=default_value,
                    is_global=is_global,
                    type=setting_type
                )

            if ENVIRONMENT != PROD_ENVIRONMENT:
                logger.debug(f'[Variables] Variable saved {key} ({default_value}) for {self.module.name}')

        deleted_count = await variables.remove_unused(
            app=app_model, exist_keys=[*app_settings.keys(), *user_settings.keys()],
        )
        logger.debug(f'[Variables] Deleted {deleted_count} unused variables for {self.module.name}')


class ModuleLogs(Component):
    """
    Module creating separate handler for save module logs to file on disk
    """
    def pre_init(self):
        pass

    async def init(self, application, app_db_model, is_created: bool):
        def filter_module_logs(x):
            matched = re.match('modules\\.(.+?(?=\\.))', x['name'])
            if matched:
                return matched.group(1) == self.module.name
        ctx: AppContext = await self.module.get_context()
        logger.add(
            LOGS_DIR / f"{self.module.name}/{self.module.name}.log",
            format=core_settings.LOGGER_FORMAT,
            rotation=core_settings.LOG_ROTATION,
            level=ctx.settings.LOG_LEVEL,
            filter=filter_module_logs,
            serialize=True,
        )

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass


class EventRoutingKeys(Component):
    async def pre_init(self):
        pass

    def __init__(self, routing_keys):
        self.routing_keys = routing_keys

    async def init(self, application, app_db_model, is_created: bool):
        await self.save_routing_keys(app_db_model)
        logger.debug(f'[RoutingKey] Routing keys saved for {self.module.name}')

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        # TODO why should I delete routing key?
        # app_model = await App.get_or_none(name=self.module.name)
        # await routing_key.filter(app=app_model).delete()
        # logger.debug(f'[{self.module.name}] Routing keys deleted')
        pass

    async def _get_or_recreate_key(self, key: str, data: dict):
        try:
            # trying to get key, raising DoesNotExist if key not exists or one of fields changed
            await routing_key.get(**data)
        except DoesNotExist:
            # delete RoutingKey for deleting by cascade users subscriptions
            await routing_key.filter(key=key).delete()

            try:
                await routing_key.create(**data)
                logger.debug(f'[RoutingKey] Created routing key {key} for {self.module.name}')
            except IntegrityError as error:
                logger.error(f'[RoutingKey] Routing key {key} create error: {error} for {self.module.name}')

    async def save_routing_keys(self, app_model):
        for key, value in self.routing_keys:
            key_data = {
                "app": app_model,
                "key": key,
                "name": value,
            }
            await self._get_or_recreate_key(key, key_data)

        deleted_num = await routing_key.remove_routing_keys_by_app(
            app_model=app_model,
            routing_keys=[value for key, value in self.routing_keys]
        )

        logger.debug(f'[RoutingKey] Deleted {deleted_num} unused routing keys for {self.module.name}')

