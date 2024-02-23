from fastapi import APIRouter, Security

from core.dependencies import get_current_user
from services.scheduler import SchedulerService

from core.schemas.task import TaskSchema
from core.utils.task import format_trigger


router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get('', response_model=list[TaskSchema])
async def get_all_tasks(task_id: str = None):
    """
    Return all available tasks
    """
    res = list()
    for task_name, task in SchedulerService.get_tasks().items():

        if task_id and task_name != task_id:
            continue

        founded_jobs = SchedulerService.get_jobs(task_name)

        res.append(
            TaskSchema(
                id=task_name,
                name=task.name,
                # module=task.module.name,
                type=task.type,
                extra_typed=task.extra_typed or None,
                trigger=format_trigger(task.trigger),
                is_has_jobs=bool(founded_jobs),
                is_available_add_job=True,
            ))
    return res
