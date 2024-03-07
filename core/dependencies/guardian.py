from fastapi.params import Query

from core import crud
from core.exceptions import NotFound


async def get_group_by_id(group_id: int = Query()):
    group = await crud.guardian_group.get(id=group_id)
    if not group:
        raise NotFound('Group not found')
    return group
