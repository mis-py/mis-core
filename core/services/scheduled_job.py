from loguru import logger
from tortoise import transactions
from core.db.dataclass import AppState, StatusTask

from core.db.models import ScheduledJob, User, Team, Module
from core.exceptions import NotFound, AlreadyExists, MISError
from core.repositories.module import IModuleRepository
from core.repositories.scheduled_job import IScheduledJobRepository
from core.schemas.task import JobCreate, JobTrigger
from core.services.base.base_service import BaseService
from core.utils.task import get_trigger
from libs.scheduler import SchedulerService
from core.utils.types import type_convert


class ScheduledJobService(BaseService):
    def __init__(self, scheduled_job_repo: IScheduledJobRepository, module_repo: IModuleRepository):
        self.scheduled_job_repo = scheduled_job_repo
        self.module_repo = module_repo
        super().__init__(repo=scheduled_job_repo)

    async def get_jobs(
            self,
            task_name: str = None,
            user_id: int = None,
            team_id: int = None,
            job_id: int = None
    ) -> list[ScheduledJob]:
        jobs = list()

        saved_jobs = await self.filter(
            id=job_id,
            task_name=task_name,
            user_id=user_id,
            team_id=team_id,
            prefetch_related=['user', 'team', 'app']
        )

        for job in saved_jobs:
            if job.status == 'running':
                # check if running task actually exist
                scheduled_jobs = SchedulerService.get_job(job.id)
            jobs.append(job)

        return jobs

    # async def get_scheduler_service_jobs(self):
    #     return SchedulerService.get_jobs()
    @transactions.atomic()
    async def create_scheduled_job(
            self,
            job_in: JobCreate,
            user: User,
            team: Team = None,
    ) -> ScheduledJob:
        [module_name, task_name] = job_in.task_name.split(':', 1)

        if not module_name or not task_name:
            raise MISError("Wrong task string specified for creating job. Must be in format 'module_name:task_name'")

        task = SchedulerService.get_task(task_name, module_name)

        # trigger logic: if specified in request - use trigger in request
        # otherwise use trigger defined by task
        # requested trigger serialized in DB as is
        # task trigger not saved in DB and constructing every time from task, so in DB in will be {"data": None}
        trigger = get_trigger(job_in.trigger)
        if not trigger and task.trigger:
            trigger = task.trigger

        module = task.module
        task_name = task.name

        if module._model.state != AppState.RUNNING:
            raise MISError("Not allowed creating job for module that is not running")

        if task.single_instance:
            scheduled_job = await self.scheduled_job_repo.get(
                task_name=task_name, app=module._model, user=user, team=team
            )
            if scheduled_job:
                raise AlreadyExists("Scheduled job already exists")

        # TODO need more validation mb
        for extra_name, extra_type in task.extra_typed.items():
            converted_value = type_convert(to_type=extra_type, value=job_in.extra[extra_name])
            job_in.extra[extra_name] = converted_value

        job_db: ScheduledJob = ScheduledJob(
            user=user,
            team=team,
            app=module._model,
            task_name=task_name,
            status=StatusTask.RUNNING if task.autostart else StatusTask.PAUSED,
            extra_data=job_in.extra,
            trigger={"data": job_in.trigger}
        )
        await self.scheduled_job_repo.save(obj=job_db)

        job_instance = await SchedulerService.add_job(
            task_name=task_name,
            module_name=module_name,
            db_id=job_db.pk,
            user=user,
            extra=job_in.extra,
            trigger=trigger
        )

        return job_db

    async def update_job_trigger(self, job_id: int, schedule_in: JobTrigger):
        job: ScheduledJob = await self.get(id=job_id, prefetch_related=['app'])
        module: Module = await self.module_repo.get(id=job.app.pk)

        task = SchedulerService.get_task(job.task_name, module.name)

        trigger = get_trigger(schedule_in.trigger)
        if not trigger and task.trigger:
            trigger = task.trigger

        await SchedulerService.reschedule_job(job_id, trigger=trigger)

        job_obj = SchedulerService.get_job(job_id)
        if job_obj.next_run_time:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'trigger': {"data": schedule_in.trigger}}
                )
            except Exception as e:
                logger.exception(e)

                # set old trigger
                old_trigger = get_trigger(job.trigger)
                if not old_trigger and task.trigger:
                    old_trigger = task.trigger
                await SchedulerService.reschedule_job(job_id, trigger=old_trigger)

        return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_paused_status(self, job_id: int):
        await SchedulerService.pause_job(job_id)

        job = SchedulerService.get_job(job_id)
        if job.next_run_time is None:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'status': StatusTask.PAUSED.value}
                )
            except Exception as e:
                logger.exception(e)
                await SchedulerService.resume_job(job_id)

        return await self.scheduled_job_repo.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_running_status(self, job_id: int):
        await SchedulerService.resume_job(job_id)

        job = SchedulerService.get_job(job_id)
        if job.next_run_time:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'status': StatusTask.RUNNING.value}
                )
            except Exception as e:
                logger.exception(e)
                await SchedulerService.pause_job(job_id)

        return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    @transactions.atomic()
    async def cancel_job(self, job_id: int):
        await SchedulerService.remove_job(job_id)

        await self.scheduled_job_repo.delete(id=job_id)

    async def filter_by_module(self, module_name: str):
        return await self.scheduled_job_repo.filter_by_module(
            module_name=module_name,
            prefetch_related=['user', 'team', 'app'],
        )
