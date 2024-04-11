import loguru

from core.db.models import ScheduledJob, User, Team, Module
from core.exceptions import NotFound, AlreadyExists
from core.schemas.task import JobCreate, JobTrigger
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from core.utils.task import get_trigger
from services.scheduler import SchedulerService

# TODO CRITICAL - should tasks start if module is disabled?

class ScheduledJobService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.scheduled_job_repo)
        self.uow = uow

    async def get_jobs(
            self,
            task_name:str = None,
            user_id:int = None,
            team_id:int = None,
            job_id:int = None
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

    async def get_scheduler_service_jobs(self):
        return SchedulerService.get_jobs()

    async def create_scheduled_job(
            self,
            job_in: JobCreate,
            user: User,
            team: Team = None,
    ) -> ScheduledJob:
        # here can be problem place coz task_name it is module.name + task.name
        task = SchedulerService.get_task(job_in.task_name)

        # trigger logic: if specified in request - use trigger in request
        # otherwise use trigger defined by task
        # requested trigger serialized in DB as is
        # task trigger not saved in DB and constructing every time from task, so in DB in will be {"data": None}
        trigger = get_trigger(job_in.trigger)
        if not trigger and task.trigger:
            trigger = task.trigger

        module = task.module
        task_name = task.name

        if task.single_instance:
            scheduled_job = await self.uow.scheduled_job_repo.get(
                task_name=task_name, app=module.model, user=user, team=team
            )
            if scheduled_job:
                raise AlreadyExists("Scheduled job already exists")

        async with self.uow:
            job_db: ScheduledJob = ScheduledJob(
                user=user,
                team=team,
                app=module.model,
                task_name=task_name,
                status=ScheduledJob.StatusTask.RUNNING if task.autostart else ScheduledJob.StatusTask.PAUSED,
                extra_data=job_in.extra,
                trigger={"data": job_in.trigger}
            )
            await self.uow.scheduled_job_repo.save(obj=job_db)

            job_instance = await SchedulerService.add_job(
                task_id=job_in.task_name,
                db_id=job_db.pk,
                user=user,
                extra=job_in.extra,
                trigger=trigger
            )

            return job_db

    async def update_job_trigger(self, job_id: int, schedule_in: JobTrigger):
        async with self.uow:
            job: ScheduledJob = await self.get(id=job_id, prefetch_related=['app'])
            module: Module = await self.uow.module_repo.get(id=job.app.pk)

            task = SchedulerService.get_task(f"{module.name}:{job.task_name}")

            trigger = get_trigger(schedule_in.trigger)
            if not trigger and task.trigger:
                trigger = task.trigger

            await SchedulerService.reschedule_job(job_id, trigger=trigger)

            updated_obj = await self.uow.scheduled_job_repo.update(
                id=job_id,
                data={'trigger': {"data": schedule_in.trigger}}
            )

            await updated_obj.save()

            return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_paused_status(self, job_id: int):
        async with self.uow:
            await SchedulerService.pause_job(job_id)

            updated_obj = await self.uow.scheduled_job_repo.update(
                id=job_id,
                data={'status': ScheduledJob.StatusTask.PAUSED.value}
            )

            await updated_obj.save()

            return await self.uow.scheduled_job_repo.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_running_status(self, job_id: int):
        async with self.uow:
            await SchedulerService.resume_job(job_id)

            updated_obj = await self.uow.scheduled_job_repo.update(
                id=job_id,
                data={'status': ScheduledJob.StatusTask.RUNNING.value}
            )

            await updated_obj.save()

            return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def cancel_job(self, job_id: int):
        async with self.uow:
            await SchedulerService.remove_job(job_id)

            await self.uow.scheduled_job_repo.delete(job_id=job_id)
