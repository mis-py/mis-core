from typing import Annotated
from fastapi.params import Depends

from core import crud
from core.exceptions import NotFound


async def get_user_by_id(user_id: int):
    user = await crud.user.get(id=user_id)
    if not user:
        raise NotFound('User not found')
    return user


async def get_team_by_id(team_id: int):
    team = await crud.team.get(id=team_id)
    if not team:
        raise NotFound('Team not found')
    return team


async def get_module_by_id(module_id: int):
    app = await crud.module.get(id=module_id)
    if not app:
        raise NotFound('Module not found')
    return app


async def get_routing_key_by_id(key_id: int):
    rk = await crud.routing_key.get(id=key_id)
    if not rk:
        raise NotFound('RoutingKey not found')
    return rk


async def pagination_parameters(skip: int = 0, limit: int = 100) -> dict:
    return {"skip": skip, "limit": limit}


PaginationDep = Annotated[dict, Depends(pagination_parameters)]
