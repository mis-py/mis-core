import loguru

from core.db.models import ScheduledJob, User, Team
from core.exceptions import NotFound, AlreadyExists
from core.schemas.task import JobCreate, JobScheduleUpdate
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork
from core.utils.task import make_trigger
from services.scheduler import SchedulerService


class ScheduledJobService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.scheduled_job_repo)
        self.uow = uow

    async def get_scheduled_jobs_dict(self) -> dict[str, ScheduledJob]:
        """
        Returns all jobs as dict {job_id: job}
        """
        scheduled_jobs = await self.filter(prefetch_related=['user', 'team', 'app'])
        scheduled_jobs_dict = {job.job_id: job for job in scheduled_jobs}
        return scheduled_jobs_dict

    async def create_scheduled_job(
            self,
            job_in: JobCreate,
            user: User,
            team: Team = None,
    ) -> ScheduledJob:

        if job_in:
            extra = job_in.extra
            trigger = make_trigger(job_in.trigger) if job_in.trigger else None
        else:
            extra = None
            trigger = None

        if job_in and job_in.trigger:
            interval = job_in.trigger.interval
            cron = job_in.trigger.cron
        else:
            interval = None
            cron = None

        task = SchedulerService.get_task(job_in.task_id)

        module = task.module
        task_name = task.name

        if task.single_instance:
            scheduled_job = await self.uow.scheduled_job_repo.get(task_name=task_name, app=module.model, user=user, team=team)
            if scheduled_job:
                raise AlreadyExists("Scheduled job already exists")

        job_db: ScheduledJob = await self.create_by_kwargs(
            user=user,
            team=team,
            app=module.model,
            task_name=task_name,
            status=ScheduledJob.StatusTask.RUNNING if task.autostart else ScheduledJob.StatusTask.PAUSED,
            extra_data=extra,
            interval=interval,
            cron=cron,
        )

        # TODO check if job created and started, if no - remove from DB?
        job_instance = await SchedulerService.add_job(
            task_id=job_in.task_id,
            db_id=job_db.pk,
            user=user,
            extra=extra,
            trigger=trigger
        )

        job_db.job_id = job_db.pk
        await job_db.save()

        return job_db

    async def update_job_trigger(self, job_id: int, schedule_in: JobScheduleUpdate):
        await self.uow.scheduled_job_repo.update(
            job_id=job_id,
            data={'interval': schedule_in.interval, 'cron': schedule_in.cron}
        )

        trigger = make_trigger(schedule_in)
        await SchedulerService.reschedule_job(job_id, trigger=trigger)

    async def set_paused_status(self, job_id: int):
        await self.uow.scheduled_job_repo.update(
            job_id=job_id,
            data={'status': ScheduledJob.StatusTask.PAUSED.value}
        )

        await SchedulerService.pause_job(job_id)

    async def set_running_status(self, job_id: int):
        await self.uow.scheduled_job_repo.update(
            job_id=job_id,
            data={'status': ScheduledJob.StatusTask.RUNNING.value}
        )

        await SchedulerService.resume_job(job_id)

    async def cancel_job(self, job_id: int):
        await self.uow.scheduled_job_repo.delete(job_id=job_id)
        await SchedulerService.remove_job(job_id)
