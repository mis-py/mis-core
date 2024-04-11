from typing import Optional

from core.schemas.task import TaskResponse
from core.utils.task import format_trigger
from services.scheduler import SchedulerService


def get_available_tasks(task_id: Optional[str] = None) -> list[TaskResponse]:
    res = list()
    for task_name, task in SchedulerService.get_tasks().items():

        if task_id and task_name != task_id:
            continue

        #founded_jobs = SchedulerService.get_jobs()

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
