from typing import Annotated
from fastapi.params import Depends, Query

from core.dependencies.uow import UnitOfWorkDep
from core.exceptions import NotFound
from core.services.guardian_service import GAccessGroupService
from core.services.user import UserService
from core.services.team import TeamService
from core.services.module import ModuleUOWService
from core.services.notification import RoutingKeyService


async def get_user_by_id(uow: UnitOfWorkDep, user_id: int):
    user = await UserService(uow).get(id=user_id)
    if not user:
        raise NotFound('User not found')
    return user


async def get_team_by_id(uow: UnitOfWorkDep, team_id: int):
    team = await TeamService(uow).get(id=team_id)
    if not team:
        raise NotFound('Team not found')
    return team


async def get_module_by_id(uow: UnitOfWorkDep, module_id: int):
    app = await ModuleUOWService(uow).get(id=module_id)
    if not app:
        raise NotFound('Module not found')
    return app


async def get_routing_key_by_id(uow: UnitOfWorkDep, key_id: int):
    rk = await RoutingKeyService(uow).get(id=key_id)
    if not rk:
        raise NotFound('RoutingKey not found')
    return rk

async def get_group_by_id(uow: UnitOfWorkDep, group_id: int = Query()):
    group = await GAccessGroupService(uow).get(id=group_id)
    if not group:
        raise NotFound('Group not found')
    return group


async def pagination_parameters(skip: int = 0, limit: int = 100) -> dict:
    return {"skip": skip, "limit": limit}


PaginationDep = Annotated[dict, Depends(pagination_parameters)]
