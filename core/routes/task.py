from typing import Annotated

from fastapi import APIRouter, Security, Query, Depends

from core.dependencies.security import get_current_user
from core.dependencies.services import get_scheduler_service

from core.schemas.task import TaskResponse
from core.services.scheduler import SchedulerService
from core.utils.schema import MisResponse

router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get(
    '',
    response_model=MisResponse[list[TaskResponse]]
)
async def get_all_tasks(
        scheduler_service: Annotated[SchedulerService, Depends(get_scheduler_service)],
        task_id: str = Query(default=None)
):
    """
    Return available tasks
    """
    tasks = scheduler_service.get_available_tasks(task_id=task_id)
    return MisResponse[list[TaskResponse]](result=tasks)
