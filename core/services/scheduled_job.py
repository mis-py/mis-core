from core.db.models import ScheduledJob, User, Team
from core.exceptions import NotFound, AlreadyExists
from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork


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
            job_id: str,
            user: User,
            team: Team = None,
            extra: dict = None,
            interval: int = None,
            cron: str = None,
    ) -> ScheduledJob:
        # extract module and task name from job_id
        jop_id_elements = job_id.split(':')
        module_name = jop_id_elements[1]
        task_name = jop_id_elements[2]

        module = await self.uow.module_repo.get(name=module_name)
        if module is None:
            raise NotFound(f"Scheduled task not created; Module '{module_name}' not found")

        scheduled_job = await self.uow.scheduled_job_repo.get(job_id=job_id)
        if scheduled_job is None:
            raise AlreadyExists("Scheduled task already exists")

        scheduled_job = await self.create_by_kwargs(
            user=user,
            team=team,
            app=module,
            job_id=job_id,
            name=task_name,
            status=ScheduledJob.StatusTask.PAUSED,
            extra_data=extra,
            interval=interval,
            cron=cron,
        )
        return scheduled_job

    async def update_job_trigger(self, job_id: str, interval: int, cron: str):
        await self.uow.scheduled_job_repo.update(
            job_id=job_id,
            data={'interval': interval, 'cron': cron}
        )

    async def set_paused_status(self, job_id: str):
        await self.uow.scheduled_job_repo.update(
            job_id=job_id,
            data={'status': ScheduledJob.StatusTask.PAUSED.value}
        )

    async def set_running_status(self, job_id: str):
        await self.uow.scheduled_job_repo.update(
            job_id=job_id,
            data={'status': ScheduledJob.StatusTask.RUNNING.value}
        )
