from fastapi import APIRouter, Security, Query

from core.dependencies.security import get_current_user

from core.schemas.task import TaskResponse
from core.services.task import get_available_tasks
from core.utils.schema import MisResponse

router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get(
    '',
    response_model=MisResponse[list[TaskResponse]]
)
async def get_all_tasks(task_id: str = Query(default=None)):
    """
    Return available tasks
    """
    tasks = get_available_tasks(task_id=task_id)
    return MisResponse[list[TaskResponse]](result=tasks)
