from fastapi import APIRouter, Depends, Security

from core.dependencies import get_current_user
from core.exceptions import NotFound

from services.scheduler import SchedulerService

from .schema import TaskSchema
# from .dependencies import get_scheduler_service
from .utils import format_trigger


router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get('/all', response_model=list[TaskSchema])
async def get_all_tasks(
        # scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """
    Return all available tasks
    """
    res = list()
    for task_name, task in SchedulerService.get_tasks():
        founded_jobs = SchedulerService.get_jobs(task_name)

        res.append(
            TaskSchema(
                id=task_name,
                name=task.name,
                module=task.module.name,
                type=task.type,
                extra_typed=task.extra_typed or None,
                trigger=format_trigger(task.trigger),
                is_has_jobs=bool(founded_jobs),
                is_available_add_job=True,
            ))
    return res


@router.get('/single', response_model=TaskSchema)
async def get_single_task(
        task_id: str = None,
        # scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """
    Get task by task_id
    :param task_id: Id of task.
    """
    task = SchedulerService.get_task(task_id)

    if not task:
        raise NotFound("Task not found!")

    founded_jobs = SchedulerService.get_jobs(task_id)

    return TaskSchema(
        id=f"{task.name}",
        name=task.name,
        module=task.module.name,
        type=task.type,
        extra_typed=task.extra_typed or None,
        trigger=format_trigger(task.trigger),
        is_has_jobs=bool(founded_jobs),
        is_available_add_job=True,
    )