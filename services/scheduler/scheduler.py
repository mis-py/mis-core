import random
from typing import Callable

from loguru import logger
from pytz import utc

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.job import Job
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.db.models import ScheduledJob
from core.utils.common import validate_task_extra

from core.exceptions import NotFound, AlreadyExists, ValidationFailed, MISError
from core.utils.task import get_trigger
from .utils import Task, job_wrapper
# from core.utils import signature_to_dict
# from core.db.helpers import StatusTask
#
# from services.modules.components import Component
from services.modules.context import AppContext

from .config import SchedulerSettings


settings = SchedulerSettings()


# TODO need to implement task type for team
class SchedulerService:
    _scheduler: AsyncIOScheduler
    # task_name (app_name + task_name), Task
    _tasks: dict[str, Task] = {}

    @classmethod
    async def init(cls, redishost='redis'):
        jobstores = {
            # 'default': RedisJobStore(db=0, host=settings.REDIS_HOST)
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor(),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }

        cls._scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=utc
        )

        cls._scheduler.start()
        cls._scheduler.remove_all_jobs()

    @classmethod
    async def close(cls):
        cls._scheduler.shutdown()

    @classmethod
    def add_task(cls, task: Task, module_name: str):
        if f"{module_name}:{task.name}" in cls._tasks:
            logger.warning(f"[ModuleService] Task already registered: {module_name}:{task.name}")
        cls._tasks[f"{module_name}:{task.name}"] = task

    @classmethod
    def get_task(cls, task_name: str, module_name: str) -> Task | None:
        if f"{module_name}:{task_name}" in cls._tasks:
            return cls._tasks[f"{module_name}:{task_name}"]
        else:
            raise NotFound(f"Task '{module_name}:{task_name}' not exist")

    # TODO what it must return?
    @classmethod
    def get_tasks(cls) -> dict[str, Task]:
        return cls._tasks

    @classmethod
    def get_job(cls, job_id: int) -> Job:
        job = cls._scheduler.get_job(str(job_id))
        if not job:
            raise NotFound(f"Job ID '{job_id}' not found")
        return job

    @classmethod
    def get_jobs(cls) -> list[Job]:
        """
        Returns list of jobs
        :return:
        """
        return cls._scheduler.get_jobs()

    @classmethod
    async def pause_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.pause()
        logger.info(f'[SchedulerService]: Pause job {job.name}')

    @classmethod
    async def resume_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.resume()
        logger.info(f'[SchedulerService]: Resume job {job.name} (next run= {job.next_run_time})')

    @classmethod
    async def create_job_instance(cls, func: Callable, job_id: int, trigger, context: AppContext, kwargs, run_at_startup=True):
        if trigger is None:
            raise MISError(f"Trigger for job '{job_id}' not specified")

        job_instance = cls._scheduler.add_job(
            job_wrapper(func),
            id=str(job_id),
            trigger=trigger,
            args=(context, ),
            kwargs=kwargs
        )

        if run_at_startup:
            job_instance.resume()
            logger.debug(f'[SchedulerService] Resume job {job_instance.name}, next run time: {job_instance.next_run_time}')
        else:
            job_instance.pause()
            logger.debug(f'[SchedulerService] Pause job {job_instance.name}')

        return job_instance

    @classmethod
    async def restore_job(cls, saved_job: ScheduledJob, module, run_at_startup) -> Job | None:
        # get declared task from saved job
        task = cls.get_task(saved_job.task_name, module.name)

        # use trigger from saved job or get default one
        trigger = get_trigger(saved_job.trigger['data'])
        if not trigger and task.trigger:
            logger.warning(f"[SchedulerService] Unknown trigger used in {saved_job.job_id}, using default one.")
            trigger = task.trigger

        # task not found, seems to be removed but job still exist
        if not task:
            logger.warning(f"[SchedulerService] Task not found! Saved job_id: {saved_job.job_id}")
            return None

        context = await module.get_context(user=saved_job.user, team=saved_job.team)

        try:
            job = await cls.create_job_instance(task.func, saved_job.pk, trigger, context, saved_job.extra_data, run_at_startup)
            logger.info(f'[SchedulerService]: Restored job {job.name}')
        except (ValueError, ConflictingIdError) as error:
            logger.error(f'[SchedulerService] Error add job: {error}')
            raise AlreadyExists(f"Conflict id, job already exists for this {task.type}")

        return job

    @classmethod
    async def add_job(cls, task_name: str, module_name:str, user, db_id: int, extra: dict = None, trigger=None) -> Job:
        task: Task = cls.get_task(task_name, module_name)

        if task.trigger is None and trigger is None:
            raise ValidationFailed(f"Argument 'trigger' required for this task!")

        if task.extra_typed and extra:
            kwargs = validate_task_extra(extra, task.extra_typed)
        elif task.extra_typed and not extra:
            raise ValidationFailed(f"Argument 'extra_typed' required some extra params {task.extra_typed}")
        else:
            kwargs = None

        context = await task.module.get_context(user=user, team=await user.team)

        try:
            job = await cls.create_job_instance(task.func, db_id, trigger, context, kwargs, task.autostart)
            logger.info(f'[SchedulerService]: Added job {job.name} {"running" if task.autostart else "paused"}')
        except ConflictingIdError:
            logger.warning(f'[SchedulerService]: Failed add job {task.name}. Job already running for this {task.type}')
            raise AlreadyExists(f"Conflict id, job already exists for this {task.type}")

        return job

    @classmethod
    async def remove_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.remove()

        logger.info(f'[SchedulerService]: Removed job {job_id}!')

    @classmethod
    async def reschedule_job(cls, job_id: int, trigger) -> None:
        job = cls.get_job(job_id)
        job.reschedule(trigger=trigger)
        logger.info(f'[SchedulerService]: Reschedule job {job_id}! (next run= {job.next_run_time})')
