from fastapi.params import Query
from core.crud import access_group
from core.exceptions import NotFound


async def get_group_by_id(group_id: int = Query()):
    group = await access_group.get(id=group_id)
    if not group:
        raise NotFound('Group not found')
    return group
