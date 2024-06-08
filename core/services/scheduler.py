from typing import Optional
from loguru import logger

from core.utils.common import validate_task_extra
from core.db.dataclass import AppState, StatusTask
from core.db.models import ScheduledJob, User, Team, Module
from core.exceptions import NotFound, AlreadyExists, MISError, ValidationFailed
from core.repositories.module import IModuleRepository
from core.repositories.scheduled_job import IScheduledJobRepository
from core.schemas.task import JobCreate, JobTrigger, TaskResponse
from core.services.base.base_service import BaseService
from core.utils.task import get_trigger, format_trigger
from core.utils.scheduler import TaskTemplate
from core.utils.module import get_app_context
from libs.schedulery import Schedulery


class SchedulerService(BaseService):
    # TODO need to implement task type for team
    _tasks: dict[str, TaskTemplate] = {}

    def __init__(self, scheduled_job_repo: IScheduledJobRepository, module_repo: IModuleRepository):
        self.scheduled_job_repo = scheduled_job_repo
        self.module_repo = module_repo
        super().__init__(repo=scheduled_job_repo)

    def add_task(self, task: TaskTemplate, module_name: str):
        if f"{module_name}:{task.name}" in self._tasks:
            logger.warning(f"[SchedulerService] Task already registered: {module_name}:{task.name}")
            return

        self._tasks[f"{module_name}:{task.name}"] = task
        logger.debug(f"[SchedulerService] Added scheduled task: {task.name} from module: {module_name}")

    def remove_task(self, task: TaskTemplate, module_name: str):
        if f"{module_name}:{task.name}" not in self._tasks:
            logger.debug(f"[SchedulerService] Task not registered: {task.name} from module: {module_name}")
            return

        del self._tasks[f"{module_name}:{task.name}"]
        logger.debug(f"[SchedulerService] Task removed: {module_name}:{task.name}")

    def get_task(self, task_name: str, module_name: str) -> TaskTemplate | None:
        if f"{module_name}:{task_name}" in self._tasks:
            return self._tasks[f"{module_name}:{task_name}"]
        else:
            raise NotFound(f"Task '{module_name}:{task_name}' not exist")

    def get_tasks(self) -> dict[str, TaskTemplate]:
        return self._tasks

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
                scheduled_jobs = Schedulery.get_job(job.id)
            jobs.append(job)

        return jobs

    async def update_job_trigger(self, job_id: int, schedule_in: JobTrigger):
        job: ScheduledJob = await self.get(id=job_id, prefetch_related=['app'])
        module: Module = await self.module_repo.get(id=job.app.pk)

        task = self.get_task(job.task_name, module.name)

        trigger = get_trigger(schedule_in.trigger)
        if not trigger and task.trigger:
            trigger = task.trigger

        Schedulery.reschedule_job(job_id, trigger=trigger)

        job_obj = Schedulery.get_job(job_id)
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
                Schedulery.reschedule_job(job_id, trigger=old_trigger)

        return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_paused_status(self, job_id: int):
        Schedulery.pause_job(job_id)

        job = Schedulery.get_job(job_id)
        if job.next_run_time is None:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'status': StatusTask.PAUSED.value}
                )
            except Exception as e:
                logger.exception(e)
                Schedulery.resume_job(job_id)

        return await self.scheduled_job_repo.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_running_status(self, job_id: int):
        Schedulery.resume_job(job_id)

        job = Schedulery.get_job(job_id)
        if job.next_run_time:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'status': StatusTask.RUNNING.value}
                )
            except Exception as e:
                logger.exception(e)
                Schedulery.pause_job(job_id)

        return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def cancel_job(self, job_id: int):
        Schedulery.remove_job(job_id)

        await self.scheduled_job_repo.delete(id=job_id)

    async def filter_by_module(self, module_name: str):
        return await self.scheduled_job_repo.filter_by_module(
            module_name=module_name,
            prefetch_related=['user', 'team', 'app'],
        )

    def get_available_tasks(self, task_id: Optional[str] = None) -> list[TaskResponse]:
        res = list()
        for task_name, task in self.get_tasks().items():

            if task_id and task_name != task_id:
                continue

            # founded_jobs = Schedulery.get_jobs()

            res.append(
                TaskResponse(
                    id=task_name,
                    name=task.name,
                    type=task.type,
                    extra_typed=task.extra_typed or {},
                    trigger=format_trigger(task.trigger),
                    #is_has_jobs=bool(founded_jobs),
                    #is_available_add_job=True,
                ))
        return res

    async def create_scheduled_job(
            self,
            job_in: JobCreate,
            user: User,
            team: Team = None,
    ) -> ScheduledJob:
        [module_name, task_name] = job_in.task_name.split(':', 1)
        task: TaskTemplate = self.get_task(task_name, module_name)

        # trigger logic: if specified in request - use trigger in request
        # otherwise use trigger defined by task
        # requested trigger serialized in DB as is
        # task trigger not saved in DB and constructing every time from task, so in DB in will be {"data": None}
        trigger = get_trigger(job_in.trigger)
        if not trigger and task.trigger:
            trigger = task.trigger

        if task.trigger is None and trigger is None:
            raise ValidationFailed(f"Argument 'trigger' required for this task!")

        task_name = task.name

        if task.single_instance:
            scheduled_job = await self.scheduled_job_repo.get(
                task_name=task_name, app=task.app, user=user, team=team
            )
            if scheduled_job:
                raise AlreadyExists("Scheduled job already exists")

        # TODO refactor this validation

        # for extra_name, extra_type in task.extra_typed.items():
        #     converted_value = type_convert(to_type=extra_type, value=job_in.extra[extra_name])
        #     job_in.extra[extra_name] = converted_value

        if task.extra_typed and job_in.extra:
            kwargs = validate_task_extra(job_in.extra, task.extra_typed)
        elif task.extra_typed and not job_in.extra:
            raise ValidationFailed(f"Argument 'extra_typed' required some extra params {task.extra_typed}")
        else:
            kwargs = None
        # ---

        job_db: ScheduledJob = ScheduledJob(
            user=user,
            team=team,
            app=task.app,
            task_name=task_name,
            status=StatusTask.RUNNING if task.autostart else StatusTask.PAUSED,
            extra_data=kwargs,
            trigger={"data": job_in.trigger}
        )
        await self.scheduled_job_repo.save(obj=job_db)

        context = await get_app_context(user=user, team=await user.team, module=task.app)

        job = Schedulery.add_job(
            task_template=task,
            job_id=job_db.id,
            kwargs=kwargs,
            trigger=trigger,
            context=context,
            run_at_startup=task.autostart
        )
        logger.info(f'[SchedulerService]: Added job [{job_db.id}]{job.name} {"running" if task.autostart else "paused"}')

        return job_db

    async def restore_jobs(self, module_name: str):
        saved_scheduled_jobs = await self.filter_by_module(module_name=module_name)
        for saved_job in saved_scheduled_jobs:
            await self.restore_job(
                saved_job=saved_job,
                module_name=module_name,
                run_at_startup=False
            )

    async def restore_job(self, saved_job: ScheduledJob, module_name, run_at_startup):
        # TODO in case of saved job has no task then do nothing?
        task = self.get_task(saved_job.task_name, module_name)

        # use trigger from saved job or get default one
        trigger = get_trigger(saved_job.trigger['data'])
        if not trigger and task.trigger:
            logger.warning(f"[SchedulerService] Unknown trigger used in {saved_job.job_id}, using default one.")
            trigger = task.trigger

        context = await get_app_context(user=saved_job.user, team=saved_job.team, module=task.app)

        job = Schedulery.add_job(
            task_template=task,
            job_id=saved_job.id,
            run_at_startup=run_at_startup,
            context=context,
            trigger=trigger,
            kwargs=saved_job.extra_data,
        )
        logger.info(f'[SchedulerService]: Restored job [{saved_job.id}]{job.name}')
