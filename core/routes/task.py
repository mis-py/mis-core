from fastapi import APIRouter, Security

from core.dependencies import get_current_user

from core.schemas.task import TaskResponse
from core.services.task import get_available_tasks

router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:tasks']),
])


@router.get('', response_model=list[TaskResponse])
async def get_all_tasks(task_id: str = None):
    """
    Return available tasks
    """
    return get_available_tasks(task_id=task_id)
