import itertools
import re
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

from config import CoreSettings
from const import DEFAULT_ADMIN_USERNAME, PROD_ENVIRONMENT, ENVIRONMENT, LOGS_DIR, MODULES_DIR
from core.db.models import ScheduledJob
from core.services.base.unit_of_work import unit_of_work_factory
from core.services.notification import RoutingKeyService
from core.services.permission import PermissionService
from core.services.scheduled_job import ScheduledJobService
from core.services.user import UserService
from core.services.variable import VariableService
from core.utils.common import pydatic_model_to_dict, signature_to_dict
from libs.modules.AppContext import AppContext

from libs.scheduler.scheduler import SchedulerService
from libs.scheduler.utils import Task
from libs.eventory.eventory import Eventory
from libs.eventory.consumer import Consumer
from libs.eventory.utils import EventTemplate
from libs.tortoise_manager import TortoiseManager
from libs.modules.Component import Component

core_settings = CoreSettings()


class TortoiseModels(Component):

    async def pre_init(self):
        logger.debug(f"[{self.module.name}] Pre-Initialising models")

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
        # await self.stop()
        self.consumers.clear()


class ScheduledTasks(Component):
    def __init__(self):
        # list of all declared tasks on init
        self._tasks: list[Task] = []

    def schedule_task(
            self,
            task_type: Literal['user', 'team'] = 'user',
            autostart: bool = False,
            single_instance: bool = False,
            *args, **kwargs
    ):
        """
        Decorator. Used for scheduling tasks.
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
            self._tasks.append(Task(
                type=task_type,
                func=func,
                trigger=trigger,
                extra_typed=extra_typed,
                autostart=autostart,
                single_instance=single_instance
            ))
            return func
        return _wrapper

    async def pre_init(self):
        pass

    async def init(self, application, app_db_model, is_created: bool):
        logger.debug(f"[{self.module.name}] Adding scheduled tasks")
        # register in SchedulerService all declared tasks and provide module for them
        for task in self._tasks:
            task.module = self.module
            SchedulerService.add_task(task, self.module.name)

        logger.debug(f"[{self.module.name}] Added scheduled tasks ")

    async def start(self):
        """
        Restore running tasks that saved in DB
        :return:
        """
        uow = unit_of_work_factory()

        saved_scheduled_jobs = await ScheduledJobService(uow).filter_by_module(module_name=self.module.name)
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
        # dependencies = [Depends(inject_context)]
        dependencies = []
        # TODO remove it if it is not used
        if not self.module.auth_disabled:
            pass
            # dependencies.append(Depends(inject_user))

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
        pass

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
        uow = unit_of_work_factory()
        admin_user = await UserService(uow).get(username=DEFAULT_ADMIN_USERNAME)

        exist_permission_ids = []
        for scope, description in self.module.permissions.items():
            perm = await PermissionService(uow).update_or_create(
                module=app_model,
                name=description,
                scope=scope,
            )
            logger.debug(f'[Variables] Created permission {scope} for {self.module.name}')

            await admin_user.add_permission(f'{app_model.name}:{scope}')
            exist_permission_ids.append(perm.id)

        logger.debug(f'[Variables] Permissions saved for {self.module.name}')

        deleted_count = await PermissionService(uow).delete_unused(
            module_id=app_model.pk, exist_ids=exist_permission_ids)
        logger.debug(f'[Variables] Deleted {deleted_count} unused permissions for {self.module.name}')

    async def save_variables(self, app_model):
        uow = unit_of_work_factory()

        app_settings, user_settings = dict(self.module_settings), dict(self.user_settings)
        settings = itertools.chain(app_settings.items(), user_settings.items())

        typed_settings = {
            **pydatic_model_to_dict(self.user_settings),
            **pydatic_model_to_dict(self.module_settings),
        }

        for key, default_value in settings:
            setting_type = typed_settings[key]["type"]
            is_global = key in app_settings
            setting, is_created = await VariableService(uow).get_or_create(
                module_id=app_model.pk,
                key=key,
                default_value=default_value,
                is_global=is_global,
                type=setting_type
            )
            if not is_created:
                await VariableService(uow).update_params(
                    variable=setting,
                    default_value=default_value,
                    is_global=is_global,
                    type=setting_type
                )

            if ENVIRONMENT != PROD_ENVIRONMENT:
                logger.debug(f'[Variables] Variable saved {key} ({default_value}) for {self.module.name}')

        deleted_count = await VariableService(uow).delete_unused(
            module_id=app_model.pk, exist_keys=[*app_settings.keys(), *user_settings.keys()],
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
            level=ctx.variables.LOG_LEVEL,
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
        pass

    async def save_routing_keys(self, app_model):
        uow = unit_of_work_factory()

        for key, value in self.routing_keys:
            routing_key = await RoutingKeyService(uow=uow).get(app_id=app_model.pk, key=key, name=value)
            if routing_key:
                logger.debug(f'[RoutingKey] Routing key {key} already created for {self.module.name}')
                continue

            try:
                await RoutingKeyService(uow=uow).recreate(module_id=app_model.pk, key=key, name=value)
                logger.debug(f'[RoutingKey] Created routing key {key} for {self.module.name}')
            except IntegrityError as error:
                logger.error(f'[RoutingKey] Routing key {key} create error: {error} for {self.module.name}')

        # TODO rk is removing right after they created. fix it
        # deleted_num = await RoutingKeyService(uow=uow).delete_unused(
        #     module_id=app_model.pk,
        #     exist_keys=[value for key, value in self.routing_keys]
        # )
        #
        # logger.debug(f'[RoutingKey] Deleted {deleted_num} unused routing keys for {self.module.name}')
