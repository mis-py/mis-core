from core.db import ScheduledJob, User, Team, App
from core.db.helpers import StatusTask
from core.db.crud.base import CRUDBase


class CRUDJobs(CRUDBase):
    async def get_or_create(self, name: str):
        return await self.model.get_or_create(
            name=name,
            defaults={"enabled": False},
        )

    async def get_scheduled_job(self, job_id: str, user: User) -> ScheduledJob | None:
        return await self.model.get_or_none(job_id=job_id, user=user).select_related('user', 'team', 'app')

    async def delete_scheduled_job(self, job_id: str, user: User) -> None:
        await self.model.filter(job_id=job_id, user=user).delete()

    async def create_scheduled_job(self, job_id: str, user: User, team: Team = None, extra: dict = None) -> ScheduledJob:
        jop_id_elements = job_id.split(':')
        app_name = jop_id_elements[1]
        task_name = jop_id_elements[2]

        app = await App.get_or_none(name=app_name)
        if not app:
            raise Exception(f"Scheduled task not created; App '{app_name}' not found")

        if await ScheduledJob.get_or_none(job_id=job_id):
            raise Exception(f"Scheduled task already exists")

        job = await self.model.create(
            user=user,
            team=team,
            app=app,
            job_id=job_id,
            name=task_name,
            status=StatusTask.PAUSED,
            extra_data=extra,
        )
        return job

    async def set_job_paused_status(self, job: ScheduledJob) -> ScheduledJob:
        # TODO fix task can be None
        job.status = StatusTask.PAUSED.value
        await job.save()
        return job

    async def set_job_running_status(self, job: ScheduledJob) -> ScheduledJob:
        # TODO fix task can be None
        job.status = StatusTask.RUNNING.value
        await job.save()
        return job

    async def get_all_scheduled_jobs(self, app_name: str) -> list[ScheduledJob]:
        """
        Return list with shceduled jobs by specific module
        :param app_name:
        :return:
        """
        return await self.model.filter(app__name=app_name).select_related('user', 'team', 'app')

    async def get_scheduled_jobs_dict(self) -> dict[str, ScheduledJob]:
        """
        Returns all jobs as dict {job_id: job}
        :return:
        """
        jobs = await self.model.all().select_related('user', 'team', 'app')
        jobs_dict = {job.job_id: job for job in jobs}
        return jobs_dict

    async def get_scheduled_jobs_ids(self, status_enum: StatusTask) -> list[ScheduledJob]:
        """
        Returns all jobs job_id with specified StatusTask
        :param status_enum:
        :return:
        """
        return await self.model.filter(status=status_enum.value).values_list('job_id', flat=True)

    async def set_pause_all_app_jobs(self, app_name: str):
        """
        Set pause for specified app_name jobs
        :param app_name:
        :return:
        """
        """"""
        tasks_for_update = []
        async for task in self.model.filter(app__name=app_name):
            task.status = StatusTask.PAUSED.value
            tasks_for_update.append(task)

        if tasks_for_update:
            await self.model.bulk_update(tasks_for_update, fields=('status',))

    async def remove_all_app_tasks(self, app_name: str):
        """
        Remove all jobs specified by app_name
        :param app_name:
        :return:
        """
        await self.model.filter(app__name=app_name).delete()

    async def save_schedule_job_trigger(self, job_id, input_trigger):
        """
        Uptade job trigger in DB
        :param job_id:
        :param input_trigger:
        :return:
        """
        job = await self.model.get_or_none(job_id=job_id)
        job.interval = input_trigger.interval
        job.cron = input_trigger.cron
        await job.save()


crud_jobs = CRUDJobs(ScheduledJob)
