from loguru import logger
from pytz import utc

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.job import Job
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.triggers.combining import OrTrigger
from typing import Literal
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.db import ScheduledJob
from core.utils import validate_task_extra
from core.db.crud import crud_jobs

from .exceptions import NotFound, AlreadyExists, ValidationFailed
from .utils import Task
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
            'default': RedisJobStore(db=0, host=settings.REDIS_HOST)
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

    @classmethod
    async def close(cls):
        cls._scheduler.shutdown()

    @classmethod
    def add_task(cls, task: Task, module):
        if f"{module.name}:{task.name}" in cls._tasks:
            logger.warning(f"[ModuleService] Task already registered: {module.name}:{task.name}")
        cls._tasks[f"{module.name}:{task.name}"] = task

    @classmethod
    def get_task(cls, task_name: str) -> Task | None:
        if task_name in cls._tasks:
            return cls._tasks[task_name]
        return None

    # TODO what it must return?
    @classmethod
    def get_tasks(cls) -> dict[str, Task]:
        return cls._tasks

    @classmethod
    def get_job(cls, job_id: str) -> Job:
        job = cls._scheduler.get_job(job_id)
        if not job:
            raise NotFound(f"[ModuleService]: Job {job_id} not found")
        return job

    @classmethod
    def get_jobs(cls, task_name: str = None) -> list[Job]:
        """
        Returns list of jobs filtered by task_name if specified
        :param task_name:
        :return:
        """
        jobs = []
        for job in cls._scheduler.get_jobs():
            if task_name and task_name not in job.id:
                continue

            jobs.append(job)

        return jobs

    @classmethod
    async def pause_job(cls, job_id: str, user) -> None:
        job = cls.get_job(job_id)
        job.pause()

        job_instance = await crud_jobs.get_scheduled_job(job_id=job_id, user=user)
        await crud_jobs.set_job_paused_status(job_instance)
        logger.info(f'[ModuleService]: Pause job {job.name}')

    @classmethod
    async def resume_job(cls, job_id: str, user) -> None:
        job = cls.get_job(job_id)
        job.resume()

        job_instance = await crud_jobs.get_scheduled_job(job_id=job_id, user=user)
        await crud_jobs.set_job_running_status(job_instance)
        logger.info(f'[ModuleService]: Resume job {job.name} (next run= {job.next_run_time})')

    @classmethod
    async def create_job_instance(cls, task: Task, job_id: str, trigger, context: AppContext, kwargs, run_at_startup=True):
        job = cls._scheduler.add_job(
            task.func,
            id=job_id,
            trigger=trigger,
            args=(context, ),
            kwargs=kwargs
        )

        if run_at_startup:
            job.resume()
            logger.debug(f'[ModuleService] Resume job {job.name}, next run time: {job.next_run_time}')
        else:
            job.pause()
            logger.debug(f'[ModuleService] Pause job {job.name}')

        return job

    @classmethod
    async def restore_job(cls, saved_job: ScheduledJob, module, run_at_startup) -> Job | None:
        # get declared task from saved job
        task = cls.get_task(saved_job.task_name)

        # use trigger from saved job or get default one
        if saved_job.interval:
            trigger = IntervalTrigger(seconds=saved_job.interval)
        elif saved_job.cron:
            trigger = OrTrigger([CronTrigger.from_crontab(c) for c in saved_job.cron])
        else:
            logger.warning(f"[ModuleService] Unknown trigger used in {saved_job.job_id}, using default one.")
            trigger = task.trigger

        # task not found, seems to be removed but job still exist
        if not task:
            logger.warning(f"[ModuleService] Task not found! Saved job_id: {saved_job.job_id}")
            return None

        context = await module.get_context(user=saved_job.user, team=saved_job.team)

        try:
            job = await cls.create_job_instance(task, saved_job.job_id, trigger, context, saved_job.extra_data, run_at_startup)
            logger.info(f'[ModuleService]: Restored job {job.name}')
        except (ValueError, ConflictingIdError) as error:
            logger.error(f'[ModuleService] Error add job: {error}')
            raise AlreadyExists(f"[ModuleService] Conflict id, job already exists for this {task.type}")

        return job

    @classmethod
    async def add_job(cls, task_id: str, user, extra: dict = None, trigger=None) -> Job:
        task = cls.get_task(task_id)
        if not task:
            raise NotFound(f"[ModuleService]: Task '{task_id}' not exist")

        if task.trigger is None and trigger is None:
            raise ValidationFailed(f"[ModuleService]: Field 'trigger' required for this task!")

        if task.extra_typed and extra:
            kwargs = validate_task_extra(extra, task.extra_typed)
        elif task.extra_typed and not extra:
            raise ValidationFailed(f"[ModuleService]: Need extra params {task.extra_typed}")
        else:
            kwargs = None

        obj_id = user.team_id if task.type == 'team' else user.id
        job_id = task.make_id(app_name=task.module.name, obj_id=obj_id, extra=extra)

        context = await task.module.get_context(user=user, team=user.team)

        try:
            job = await cls.create_job_instance(task, task_id, trigger, context, kwargs, False)
            logger.info(f'[ModuleService]: Added job {job.name} (paused)')
        except ConflictingIdError:
            logger.warning(f'[ModuleService]: Failed add job {task.name}. Job already running for this {task.type}')
            raise AlreadyExists(f"[ModuleService] Conflict id, job already exists for this {task.type}")

        # save it in database
        team = await user.team if task.type == 'team' else None
        await crud_jobs.create_scheduled_job(job_id=job_id, user=user, team=team, extra=extra)
        return job

    @classmethod
    async def remove_job(cls, job_id: str, user) -> None:
        job = cls.get_job(job_id)
        job.remove()

        saved_job = await crud_jobs.get_scheduled_job(job_id=job_id, user=user)
        if not saved_job:
            raise NotFound(f"[ModuleService] Saved job {job_id} not found")

        await crud_jobs.delete_scheduled_job(job_id=job_id, user=user)
        logger.info(f'[ModuleService]: Removed job {job_id}!')
