from typing import Annotated

from fastapi.params import Path, Depends

from core.db import crud
from core.exceptions import NotFound


async def get_user_by_id(user_id: int = Path()):
    user = await crud.user.get(id=user_id)
    if not user:
        raise NotFound('User not found')
    return user


async def get_team_by_id(team_id: int = Path()):
    team = await crud.team.get(id=team_id)
    if not team:
        raise NotFound('Team not found')
    return team


async def get_app_by_id(app_id: int = Path()):
    app = await crud.app.get(id=app_id)
    if not app:
        raise NotFound('App not found')
    return app


async def get_routing_key_by_id(key_id: int = Path()):
    routing_key = await crud.routing_key.get(id=key_id)
    if not routing_key:
        raise NotFound('RoutingKey not found')
    return routing_key


async def pagination_parameters(skip: int = 0, limit: int = 100) -> dict:
    return {"skip": skip, "limit": limit}


PaginationDep = Annotated[dict, Depends(pagination_parameters)]
