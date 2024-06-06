import random
from typing import Callable
from loguru import logger
from pytz import utc
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.job import Job
from apscheduler.jobstores.base import ConflictingIdError

from core.exceptions import NotFound, AlreadyExists, MISError
from core.utils.scheduler import job_wrapper, TaskTemplate

from .config import SchedulerSettings


settings = SchedulerSettings()


class Schedulery:
    _scheduler: AsyncIOScheduler

    @classmethod
    async def init(cls):
        job_stores = {
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
            jobstores=job_stores,
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
    def pause_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.pause()
        logger.info(f'[Schedulery]: Pause job {job.name}')

    @classmethod
    def resume_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.resume()
        logger.info(f'[Schedulery]: Resume job {job.name} (next run= {job.next_run_time})')

    @classmethod
    def add_job(
            cls,
            task_template: TaskTemplate,
            job_id: int,
            kwargs: dict = None,
            trigger=None,
            context=None,
            run_at_startup=False
    ) -> Job:
        if trigger is None:
            raise MISError(f"Trigger for job '{job_id}' not specified")

        try:
            job = cls._scheduler.add_job(
                job_wrapper(task_template.func),
                id=str(job_id),
                trigger=trigger,
                args=(context,),
                kwargs=kwargs
            )
        except (ValueError, ConflictingIdError):
            logger.warning(
                f'[Schedulery]: Failed add job {task_template.name}. Job already running for this {task_template.type}')
            raise AlreadyExists(f"Conflict id, job already exists for this {task_template.type}")

        if run_at_startup:
            job.resume()
            logger.debug(
                f'[Schedulery] Resume job {job.name}, next run time: {job.next_run_time}')
        else:
            job.pause()
            logger.debug(f'[Schedulery] Pause job {job.name}')

        return job

    @classmethod
    def remove_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.remove()

        logger.info(f'[Schedulery]: Removed job {job_id}!')

    @classmethod
    def reschedule_job(cls, job_id: int, trigger) -> None:
        job = cls.get_job(job_id)
        job.reschedule(trigger=trigger)
        logger.info(f'[Schedulery]: Reschedule job {job_id}! (next run= {job.next_run_time})')
