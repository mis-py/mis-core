from typing import Literal

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from libs.schedulery import Schedulery

from core.db.dataclass import StatusTask
from core.dependencies.services import get_scheduler_service
from core.services.scheduler import SchedulerService
from core.utils.common import signature_to_dict
from core.utils.scheduler import TaskTemplate

from ..Base.BaseComponent import BaseComponent
# from core.db import ScheduledJob
# from core.utils import validate_task_extra


class ScheduledTasks(BaseComponent):
    def __init__(self):
        # list of all declared tasks on init
        self._tasks: list[TaskTemplate] = []

    def schedule_task(
            self,
            task_type: Literal['user', 'team'] = 'user',
            autostart: bool = False,
            single_instance: bool = False,
            *args, **kwargs
    ):
        """
        Decorator. Used for scheduling tasks.
        :param autostart:
        :param single_instance:
        :param task_type:
        :param args:
        :param kwargs:
        :return:
        """
        if 'trigger' in kwargs and (isinstance(kwargs['trigger'], BaseTrigger) or kwargs['trigger'] is None):
            trigger = kwargs['trigger']
        elif any(arg in kwargs for arg in ('seconds', 'hours', 'minutes')):
            trigger = IntervalTrigger(**kwargs)
        elif (arg in kwargs for arg in ('second', 'hour', 'minute')):
            trigger = CronTrigger(**kwargs, )
        else:
            raise ValueError(f"scheduled task got invalid kwargs: {kwargs}")

        def _wrapper(func):
            extra_typed = signature_to_dict(func)
            extra_typed.pop("ctx", False)
            self._tasks.append(TaskTemplate(
                type=task_type,
                func=func,
                trigger=trigger,
                extra_typed=extra_typed,
                autostart=autostart,
                single_instance=single_instance
            ))
            return func
        return _wrapper

    def extend(self, tasks: list[TaskTemplate]):
        self._tasks.extend(tasks)

    async def pre_init(self, application):
        pass

    async def init(self, app_db_model, is_created: bool):
        pass

    async def start(self):
        """
        Run tasks that saved in DB and was in StatusTask.RUNNING state
        :return:
        """
        scheduler_service: SchedulerService = get_scheduler_service()

        # add all task templates to sheduler service
        for task in self._tasks:
            task.app = self.module._model
            scheduler_service.add_task(task=task, module_name=self.module.name)

        # restore jobs from memory in paused state
        await scheduler_service.restore_jobs(module_name=self.module.name)

        # run task if saved state was RUNNING
        saved_scheduled_jobs = await scheduler_service.filter_by_module(module_name=self.module.name)
        for saved_job in saved_scheduled_jobs:
            if saved_job.status == StatusTask.RUNNING:
                Schedulery.resume_job(saved_job.pk)

    async def stop(self):
        """
        Set pause for all tasks that saved in DB
        :return:
        """
        scheduler_service: SchedulerService = get_scheduler_service()
        saved_scheduled_jobs = await scheduler_service.filter_by_module(module_name=self.module.name)
        for saved_job in saved_scheduled_jobs:
            Schedulery.pause_job(saved_job.pk)

        for task in self._tasks:
            scheduler_service.remove_task(task=task, module_name=self.module.name)

    async def shutdown(self):
        pass
