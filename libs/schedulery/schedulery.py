from typing import Callable
from loguru import logger
from pytz import utc
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.job import Job
from apscheduler.jobstores.base import ConflictingIdError


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
            raise ValueError(f"Job ID '{job_id}' not found")
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
        logger.info(f"[Schedulery]: Pause job '{job_id}' {job.name}")

    @classmethod
    def resume_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.resume()
        logger.info(f"[Schedulery]: Resume job '{job_id}' {job.name} (next run= {job.next_run_time})")

    @classmethod
    def add_job(
            cls,
            func: Callable,
            job_id: int,
            job_name: str,
            kwargs: dict = None,
            trigger=None,
            context=None,
            job_meta=None,
            run_at_startup=False,
    ) -> Job:
        if trigger is None:
            raise ValueError(f"Trigger for job '{job_id}' not specified")

        job_kwargs = dict()
        if kwargs:
            job_kwargs.update(**kwargs)
        if context:
            job_kwargs.update({'ctx': context})
        if job_meta:
            job_kwargs.update({'job_meta': job_meta})

        try:
            job = cls._scheduler.add_job(
                func,
                name=job_name,
                id=str(job_id),
                trigger=trigger,
                kwargs=job_kwargs
            )
        except (ValueError, ConflictingIdError) as e:
            logger.warning(
                f"[Schedulery]: Job with id '{job_id}' {job_name} already exists")
            raise ValueError(f"Job with id {job_id} already exists")

        if run_at_startup:
            cls.resume_job(job_id)
        else:
            cls.pause_job(job_id)

        return job

    @classmethod
    def remove_job(cls, job_id: int) -> None:
        job = cls.get_job(job_id)
        job.remove()

        logger.info(f"[Schedulery]: Removed job '{job_id}' {job.name}")

    @classmethod
    def reschedule_job(cls, job_id: int, trigger) -> None:
        job = cls.get_job(job_id)
        job.reschedule(trigger=trigger)
        logger.info(f"[Schedulery]: Reschedule job '{job_id}' {job.name} (next run= {job.next_run_time})")
